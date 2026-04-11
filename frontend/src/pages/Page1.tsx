import { useEffect, useRef, useState } from "react";
import "./Page1.css";
import { API_BASE_URL } from "../constants/constants";
import "@fortawesome/fontawesome-free/css/all.min.css";
import ReactMarkdown from "react-markdown";

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

const cleanAssistantText = (text: string) => {
  return text
    .replace(/^Brief Answer:\s*/gim, "")
    .replace(/^Brief answer:\s*/gim, "")
    .replace(/^Detailed Explanation:\s*/gim, "")
    .replace(/^Detailed explanation:\s*/gim, "")
    .replace(/^References:\s*/gim, "")
    .replace(/^\[\d+\]\s.*$/gm, "")
    .replace(/\[Source:[^\]]*\]/gi, "")
    .replace(/\[\d+:\s*[^\]]*\]/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
};
const Page1 = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [loading, setLoading] = useState(false);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const activeChat = JSON.parse(
      localStorage.getItem("betesbot_active_chat") || "null"
    );

    if (activeChat) {
      setMessages([
        { role: "user", text: activeChat.prompt },
        {
          role: "assistant",
          text: activeChat.reply,
          citations: activeChat.citations || []
        }
      ]);
      setHasStartedChat(true);
    } else {
      setMessages([]);
      setHasStartedChat(false);
    }
  }, []);

  const saveChatToHistory = (
    prompt: string,
    reply: string,
    citations: Citation[] = []
  ) => {
    const existing = JSON.parse(localStorage.getItem("betesbot_history") || "[]");

    const newChat = {
      id: Date.now(),
      prompt,
      reply,
      citations,
      createdAt: new Date().toLocaleString(),
    };

    localStorage.setItem(
      "betesbot_history",
      JSON.stringify([newChat, ...existing])
    );

    localStorage.setItem("betesbot_active_chat", JSON.stringify(newChat));
  };

  const handleStop = () => {
    controllerRef.current?.abort();
    controllerRef.current = null;
  };

  const handleSend = async (customMessage?: string) => {
    const finalMessage = customMessage ?? message;
    if (!finalMessage.trim() || loading) return;

    const abortController = new AbortController();
    controllerRef.current = abortController;

    setLoading(true);
    setHasStartedChat(true);

    setMessages((prev) => [
      ...prev,
      { role: "user", text: finalMessage },
      { role: "assistant", text: "__loading__" }
    ]);

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: finalMessage }),
        signal: abortController.signal,
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data = await res.json();
      console.log("API response:", data);

      const rawAssistantText =
        data.answer ||
        data.response ||
        data.message ||
        data.reply ||
        "No response returned from server.";

      const assistantText = cleanAssistantText(rawAssistantText);

      const assistantCitations =
        data.citations ||
        data.sources ||
        data.references ||
        [];

      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1 &&
          msg.role === "assistant" &&
          msg.text === "__loading__"
            ? {
                role: "assistant",
                text: assistantText,
                citations: assistantCitations
              }
            : msg
        )
      );

      saveChatToHistory(finalMessage, assistantText, assistantCitations);
    } catch (err) {
      const error = err as Error;
      const errorMessage = "Error: " + error.message;

      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1 &&
          msg.role === "assistant" &&
          msg.text === "__loading__"
            ? { role: "assistant", text: errorMessage }
            : msg
        )
      );
    } finally {
      controllerRef.current = null;
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
                  {msg.text === "__loading__" ? (
                    <div className="loader"></div>
                  ) : (
                    <>
                      <div className="response-answer">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>

                      {msg.citations && msg.citations.length > 0 && (
                        <div className="citations">
                          <h3 className="citations-title">References</h3>
                          <ul className="citations-list">
                            {msg.citations.map((cite, i) => (
                              <li key={i}>
                                {typeof cite === "string"
                                  ? cite
                                  : cite.url ? (
                                      <a
                                        href={cite.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                      >
                                        {cite.source ?? cite.url}
                                      </a>
                                    ) : (
                                      cite.source ?? JSON.stringify(cite)
                                    )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
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
              if (loading) {
                handleStop();
              } else {
                handleSend();
              }
            }
          }}
          className="chat-input"
        />

        <button
          onClick={loading ? handleStop : () => handleSend()}
          className="send-btn"
        >
          {loading ? (
            <i className="fa-solid fa-square"></i>
          ) : (
            <i className="fa-solid fa-arrow-up"></i>
          )}
        </button>
      </div>
    </div>
  );
};

export default Page1;