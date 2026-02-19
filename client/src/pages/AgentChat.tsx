import { useState, useRef, useEffect } from "react";
import { useParams } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Spinner } from "@/components/ui/spinner";
import { Send, Zap, Settings, RotateCcw, Mic } from "lucide-react";
import { toast } from "sonner";
import { Streamdown } from "streamdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  executionId?: string;
}

interface ExecutionResult {
  executionId: string;
  language: string;
  code: string;
  success: boolean;
  output: string;
  error?: string;
  duration: number;
  exitCode: number;
}

export default function AgentChat() {
  const params = useParams<{ sessionId?: string }>();
  const sessionId = params?.sessionId || `session-${Date.now()}`;
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [autoExecute, setAutoExecute] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<ExecutionResult[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    
    // Add user message to chat
    const newMessage: Message = {
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setIsLoading(true);

    try {
      // Use WebSocket for streaming
      const ws = new WebSocket(
        `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/chat/${sessionId}`
      );

      let assistantMessage = "";

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            message: userMessage,
            auto_execute: autoExecute,
          })
        );
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "chunk") {
          assistantMessage += data.content;
          // Update the last message in real-time
          setMessages((prev) => {
            const updated = [...prev];
            if (updated[updated.length - 1]?.role === "assistant") {
              updated[updated.length - 1].content = assistantMessage;
            }
            return updated;
          });
        } else if (data.type === "complete") {
          if (data.execution_history) {
            setExecutionHistory(data.execution_history);
          }
          ws.close();
          setIsLoading(false);
        } else if (data.type === "error") {
          toast.error(`Error: ${data.error}`);
          ws.close();
          setIsLoading(false);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        toast.error("Connection error");
        setIsLoading(false);
      };

      ws.onclose = () => {
        setIsLoading(false);
      };

      // Add assistant message placeholder
      const assistantMsg: Message = {
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message");
      setIsLoading(false);
    }
  };

  const startVoiceInput = async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        const chunks: Blob[] = [];

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
          const blob = new Blob(chunks, { type: "audio/webm" });
          // TODO: Send to Whisper API for transcription
          toast.info("Voice input recorded (transcription coming soon)");
          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        toast.error("Microphone access denied");
      }
    } else {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
      }
    }
  };

  const clearChat = () => {
    setMessages([]);
    setExecutionHistory([]);
    toast.success("Chat cleared");
  };

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <div className="w-64 border-r border-border bg-card p-4 flex flex-col">
        <div className="mb-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            Agent Pro
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Autonomous AI Agent
          </p>
        </div>

        <div className="space-y-3 flex-1">
          <Button
            variant="outline"
            className="w-full justify-start"
            onClick={clearChat}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            New Chat
          </Button>

          <div className="border-t border-border pt-3">
            <h3 className="text-sm font-semibold mb-2">Settings</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoExecute}
                  onChange={(e) => setAutoExecute(e.target.checked)}
                  className="w-4 h-4"
                />
                <span className="text-sm">Auto Execute Code</span>
              </label>
            </div>
          </div>
        </div>

        <div className="border-t border-border pt-3">
          <p className="text-xs text-muted-foreground">
            Session: {sessionId.slice(0, 8)}...
          </p>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card p-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Chat</h2>
            <p className="text-sm text-muted-foreground">
              {messages.length} messages
            </p>
          </div>
          <Button variant="ghost" size="icon">
            <Settings className="w-5 h-5" />
          </Button>
        </div>

        {/* Messages Area */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <Zap className="w-12 h-12 text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">
                  Welcome to Agent Pro
                </h3>
                <p className="text-muted-foreground max-w-md">
                  Start by typing a task or question. The agent will help you
                  execute code, analyze data, and automate tasks.
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-2xl rounded-lg p-4 ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-card border border-border text-foreground"
                    }`}
                  >
                    {msg.role === "assistant" ? (
                      <Streamdown>{msg.content}</Streamdown>
                    ) : (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    )}
                    <p className="text-xs mt-2 opacity-70">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-card border border-border rounded-lg p-4">
                  <Spinner className="w-5 h-5" />
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>

        {/* Execution History Tab */}
        {executionHistory.length > 0 && (
          <div className="border-t border-border bg-card p-4">
            <Tabs defaultValue="executions" className="w-full">
              <TabsList>
                <TabsTrigger value="executions">
                  Executions ({executionHistory.length})
                </TabsTrigger>
              </TabsList>
              <TabsContent value="executions" className="mt-4">
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {executionHistory.map((exec, idx) => (
                    <Card key={idx} className="p-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-mono">
                          {exec.language}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            exec.success
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {exec.success ? "Success" : "Failed"}
                        </span>
                      </div>
                      {exec.output && (
                        <p className="text-xs text-muted-foreground mt-1 font-mono line-clamp-2">
                          {exec.output}
                        </p>
                      )}
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-border bg-card p-4">
          <form onSubmit={sendMessage} className="flex gap-2 max-w-4xl mx-auto">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me to execute code, analyze data, or automate tasks..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={startVoiceInput}
              className={isRecording ? "bg-red-500 text-white" : ""}
            >
              <Mic className="w-5 h-5" />
            </Button>
            <Button type="submit" disabled={isLoading || !input.trim()}>
              <Send className="w-4 h-4 mr-2" />
              Send
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
