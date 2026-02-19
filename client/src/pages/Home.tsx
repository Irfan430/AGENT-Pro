import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Zap, Code2, Brain, Cpu, Shield } from "lucide-react";

export default function Home() {
  const [, setLocation] = useLocation();

  const features = [
    {
      icon: Code2,
      title: "Multi-Language Code Execution",
      description: "Execute Python, JavaScript, Shell, Java, R, and Ruby code safely",
    },
    {
      icon: Brain,
      title: "AI-Powered Task Planning",
      description: "Automatic task decomposition and multi-step workflow execution",
    },
    {
      icon: Cpu,
      title: "Self-Healing Execution",
      description: "Automatic error detection and intelligent code correction",
    },
    {
      icon: Shield,
      title: "Safe Execution",
      description: "Sandboxed execution with safety validation and user approval",
    },
    {
      icon: Zap,
      title: "Real-time Streaming",
      description: "Live response streaming with WebSocket support",
    },
    {
      icon: Zap,
      title: "Voice Input",
      description: "Hands-free interaction with Whisper API integration",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-blue-500" />
            <h1 className="text-2xl font-bold">Agent Pro</h1>
          </div>
          <Button onClick={() => setLocation("/chat")} className="bg-blue-600 hover:bg-blue-700">
            Launch Agent
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Autonomous AI Agent Pro
        </h2>
        <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
          Complete control over your device through natural language commands. Execute code, analyze data, and automate tasks with DeepSeek AI.
        </p>
        <Button
          onClick={() => setLocation("/chat")}
          size="lg"
          className="bg-blue-600 hover:bg-blue-700 text-lg px-8"
        >
          Start Using Agent Pro
        </Button>
      </section>

      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold mb-12 text-center">Powerful Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <Card key={idx} className="bg-slate-800 border-slate-700 p-6 hover:border-blue-500 transition">
                <Icon className="w-8 h-8 text-blue-500 mb-4" />
                <h4 className="text-lg font-semibold mb-2">{feature.title}</h4>
                <p className="text-slate-400">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-6xl mx-auto px-4 py-16 text-center">
        <h3 className="text-3xl font-bold mb-6">Ready to Get Started?</h3>
        <p className="text-slate-300 mb-8 max-w-2xl mx-auto">
          Launch the agent and start executing tasks with natural language commands.
        </p>
        <Button
          onClick={() => setLocation("/chat")}
          size="lg"
          className="bg-purple-600 hover:bg-purple-700 text-lg px-8"
        >
          Open Agent Chat
        </Button>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900/50 mt-20 py-8 text-center text-slate-400">
        <p>Autonomous Agent Pro 2026 | Powered by DeepSeek AI</p>
      </footer>
    </div>
  );
}
