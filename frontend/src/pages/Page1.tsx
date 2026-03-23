import { useState } from "react";
import "./Page1.css";
import { API_BASE_URL } from "../constants/constants";

const quickPrompts = [
  {
    title: "Check Symptoms",
    description: "Understand common diabetes symptoms",
    prompt: "What are the common symptoms of diabetes?"
  },
  {
    title: "Blood Sugar Guide",
    description: "View normal ranges and what your levels may mean",
    prompt: "What are normal blood sugar ranges?"
  },
  {
    title: "Diet Recommendations",
    description: "Get food suggestions and meal guidance for diabetes",
    prompt: "What foods are recommended for someone with diabetes?"
  },
  {
    title: "Title Later",
    description: "Paragraph later",
    prompt: "Give me general diabetes management advice."
  }
];

const Page1 = () => {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  type Citation = { source?: string; content?: string; url?: string; score?: number } | string;
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);

  const saveChatToHistory = (prompt: string, reply: string) => {
    const existing = JSON.parse(localStorage.getItem("betesbot_history") || "[]");

    const newChat = {
      id: Date.now(),
      prompt,
      reply,
      createdAt: new Date().toLocaleString(),
    };

    localStorage.setItem(
      "betesbot_history",
      JSON.stringify([newChat, ...existing])
    );
  };

  const handleSend = async (customMessage?: string) => {
    const finalMessage = customMessage ?? message;

    if (!finalMessage.trim()) return;

    setLoading(true);
    setAnswer("");
    setCitations([]);

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: finalMessage }),
      });
      const data = await res.json();

      setAnswer(data.answer ?? "");
      setCitations(data.citations ?? []);
      saveChatToHistory(finalMessage, data.answer ?? "");
    } catch (err) {
      const errorMessage = "Error: " + (err as Error).message;
      setAnswer(errorMessage);
      saveChatToHistory(finalMessage, errorMessage);
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  return (
    <div className="chat-container">
      <h1 className="page-title">Ask about diabetes!</h1>

      <div className="quick-actions">
        {quickPrompts.map((item) => (
          <button
            key={item.title}
            className="quick-action-card"
            onClick={() => {
              setMessage(item.prompt);
              handleSend(item.prompt);
            }}
            disabled={loading}
          >
            <span className="quick-action-title">{item.title}</span>
            <span className="quick-action-description">{item.description}</span>
          </button>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          placeholder="Type your question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSend();
            }
          }}
          className="chat-input"
        />

        <button onClick={() => handleSend()} className="send-btn" disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>

      {answer && (
        <div className="response-container">
          <p className="response-answer">{answer}</p>
          {citations.length > 0 && (
            <div className="citations">
              <h3 className="citations-title">References</h3>
              <ul className="citations-list">
                {citations.map((cite, i) => (
                  <li key={i}>
                    {typeof cite === "string"
                      ? cite
                      : cite.url
                      ? <a href={cite.url} target="_blank" rel="noopener noreferrer">{cite.source ?? cite.url}</a>
                      : cite.source ?? JSON.stringify(cite)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Page1;
