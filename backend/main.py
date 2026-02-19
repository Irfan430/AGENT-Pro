"""
Main FastAPI server for Autonomous Agent Pro.
Provides REST API and WebSocket endpoints for agent interaction.
"""

import logging
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.config import settings
from backend.agent.agent_core import AutonomousAgent
from backend.executor.code_executor import code_executor
from backend.llm.llm_manager import llm_manager

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Store active sessions
active_sessions: dict[str, AutonomousAgent] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    logger.info(f"Execution Mode: {settings.EXECUTION_MODE}")
    yield
    logger.info("Shutting down application")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI Agent with multi-language code execution",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Pydantic models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: Optional[str] = None
    auto_execute: bool = False


class ExecuteCodeRequest(BaseModel):
    """Code execution request model."""
    code: str
    language: str
    timeout: Optional[int] = None


class TaskPlanRequest(BaseModel):
    """Task plan request model."""
    task_description: str
    context: Optional[str] = None


class SessionRequest(BaseModel):
    """Session management request model."""
    session_id: str


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER.value,
    }


# REST API Endpoints

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint for single message interaction.
    
    Args:
        request: ChatRequest with message and optional session_id
    
    Returns:
        JSON response with assistant's reply
    """
    try:
        session_id = request.session_id or "default"
        
        # Get or create agent session
        if session_id not in active_sessions:
            active_sessions[session_id] = AutonomousAgent(session_id)
        
        agent = active_sessions[session_id]
        
        # Get response from agent
        response = await agent.chat(
            request.message,
            stream=False,
            auto_execute=request.auto_execute,
        )
        
        return {
            "session_id": session_id,
            "response": response,
            "execution_history": agent.get_execution_history(),
        }
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute")
async def execute_code(request: ExecuteCodeRequest):
    """
    Execute code endpoint.
    
    Args:
        request: ExecuteCodeRequest with code and language
    
    Returns:
        JSON response with execution result
    """
    try:
        # Validate code syntax
        is_valid, error = code_executor.validate_code_syntax(
            request.code,
            request.language,
        )
        
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "output": "",
            }
        
        # Execute code
        result = await code_executor.execute(
            request.code,
            request.language,
            request.timeout,
        )
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Error in execute endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task-plan")
async def create_task_plan(request: TaskPlanRequest):
    """
    Create a task plan endpoint.
    
    Args:
        request: TaskPlanRequest with task description
    
    Returns:
        JSON response with task plan
    """
    try:
        agent = AutonomousAgent()
        plan = await agent.create_task_plan(
            request.task_description,
            request.context,
        )
        
        return plan.to_dict()
    
    except Exception as e:
        logger.error(f"Error in task plan endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-plan")
async def execute_task_plan(request: TaskPlanRequest):
    """
    Execute a task plan endpoint.
    
    Args:
        request: TaskPlanRequest with task description
    
    Returns:
        JSON response with execution results
    """
    try:
        agent = AutonomousAgent()
        plan = await agent.create_task_plan(request.task_description)
        result = await agent.execute_task_plan(plan)
        
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Error in execute plan endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session ID
    
    Returns:
        JSON response with conversation history
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        agent = active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "conversation_history": agent.get_conversation_history(),
            "execution_history": agent.get_execution_history(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/{session_id}/clear")
async def clear_session(session_id: str):
    """
    Clear conversation history for a session.
    
    Args:
        session_id: Session ID
    
    Returns:
        JSON response confirming clear
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        agent = active_sessions[session_id]
        agent.clear_history()
        
        return {"success": True, "session_id": session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.
    
    Args:
        session_id: Session ID
    
    Returns:
        JSON response confirming deletion
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del active_sessions[session_id]
        
        return {"success": True, "session_id": session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat with streaming responses.
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID
    """
    await websocket.accept()
    
    # Get or create agent session
    if session_id not in active_sessions:
        active_sessions[session_id] = AutonomousAgent(session_id)
    
    agent = active_sessions[session_id]
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            auto_execute = message_data.get("auto_execute", False)
            
            if not user_message:
                await websocket.send_json({
                    "type": "error",
                    "error": "Empty message",
                })
                continue
            
            try:
                # Stream response from agent
                async for chunk in await agent.chat(
                    user_message,
                    stream=True,
                    auto_execute=auto_execute,
                ):
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk,
                    })
                
                # Send completion message
                await websocket.send_json({
                    "type": "complete",
                    "execution_history": agent.get_execution_history(),
                })
            
            except Exception as e:
                logger.error(f"Error in WebSocket chat: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "error": str(e),
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
    )
