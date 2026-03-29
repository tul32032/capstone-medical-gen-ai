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

type Citation =
  | { source?: string; content?: string; url?: string; score?: number }
  | string;

type Message = {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
};

const Page1 = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [hasStartedChat, setHasStartedChat] = useState(false);
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
      setHasStartedChat(true);

      setMessages((prev) => [
        ...prev,
        { role: "user", text: finalMessage }
      ]);

      try {
        const res = await fetch(`${API_BASE_URL}/api/chat/`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: finalMessage }),
        });

        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }

        const data = await res.json();
        console.log("API response:", data);

        const assistantText =
          data.answer ||
          data.response ||
          data.message ||
          data.reply ||
          "No response returned from server.";

        const assistantCitations =
          data.citations ||
          data.sources ||
          data.references ||
          [];

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: assistantText,
            citations: assistantCitations
          }
        ]);

        saveChatToHistory(finalMessage, assistantText);
      } catch (err) {
        const errorMessage = "Error: " + (err as Error).message;

        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: errorMessage }
        ]);
      } finally {
        setLoading(false);
        setMessage("");
      }
    };

  return (
    <div className="chat-container">
      {!hasStartedChat && (
        <h1 className="page-title">Ask about diabetes!</h1>
      )}

      {!hasStartedChat && (
        <div className="quick-actions">
          {quickPrompts.map((item) => (
            <button
              key={item.title}
              className="quick-action-card"
              onClick={() => handleSend(item.prompt)}
              disabled={loading}
            >
              <span className="quick-action-title">{item.title}</span>
              <span className="quick-action-description">
                {item.description}
              </span>
            </button>
          ))}
        </div>
      )}

      {hasStartedChat && (
        <div className="chat-thread">
          {messages.map((msg, index) =>
            msg.role === "user" ? (
              <div key={index} className="user-message-row">
                <div className="user-message-bubble">{msg.text}</div>
              </div>
            ) : (
              <div key={index} className="assistant-message-row">
                <div className="assistant-message-bubble">
                  <p className="response-answer">{msg.text}</p>

                  {msg.citations && msg.citations.length > 0 && (
                    <div className="citations">
                      <h3 className="citations-title">References</h3>
                      <ul className="citations-list">
                        {msg.citations.map((cite, i) => (
                          <li key={i}>
                            {typeof cite === "string"
                              ? cite
                              : cite.url
                              ? (
                                  <a
                                    href={cite.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    {cite.source ?? cite.url}
                                  </a>
                                )
                              : cite.source ?? JSON.stringify(cite)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )
          )}
        </div>
      )}

      <div
        className={`chat-input-container ${
          hasStartedChat ? "chat-input-after-send" : ""
        }`}
      >
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

        <button
          onClick={() => handleSend()}
          className="send-btn"
          disabled={loading}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default Page1;