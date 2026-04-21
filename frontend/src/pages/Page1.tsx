import { useEffect, useRef, useState } from "react";
import "./Page1.css";
import { API_BASE_URL } from "../constants/constants";
import "@fortawesome/fontawesome-free/css/all.min.css";
import ReactMarkdown from "react-markdown";

const quickPrompts = [
  {
    title: "Check Symptoms",
    description: "Understand common diabetes symptoms",
    prompt: "What are the common symptoms of diabetes?",
    icon: "fa-solid fa-stethoscope",
  },
  {
    title: "Blood Sugar Guide",
    description: "View normal ranges and what your levels may mean",
    prompt: "What are normal blood sugar ranges?",
    icon: "fa-solid fa-chart-column",
  },
  {
    title: "Diet Recommendations",
    description: "Get food suggestions and meal guidance for diabetes?",
    prompt: "What foods are recommended for someone with diabetes?",
    icon: "fa-solid fa-bowl-food",
  },
  {
    title: "Title Later",
    description: "Paragraph later",
    prompt: "Give me general diabetes management advice.",
    icon: "fa-solid fa-clipboard-check",
  },
];

type Citation =
  | { source?: string; content?: string; url?: string; score?: number }
  | string;

type Message = {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
};

const formatAssistantText = (input: string) => {
  return input
    .replace(/^Brief Answer:\s*/gim, "")
    .replace(/^Detailed Explanation:\s*/gim, "")
    .replace(/^References:\s*/gim, "")
    .replace(/^\[\d+\]\s.*$/gm, "")
    .replace(/\[Source:[^\]]*\]/gi, "")
    .replace(/\[\d+:\s*[^\]]*\]/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
};

const Page1 = () => {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState<Message[]>([]);
  const [started, setStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const stored = JSON.parse(
      localStorage.getItem("betesbot_active_chat") || "null"
    );

    if (stored) {
      if (stored.messages) {
        setChat(stored.messages);
      } else {
        setChat([
          { role: "user", text: stored.prompt },
          {
            role: "assistant",
            text: stored.reply,
            citations: stored.citations || [],
          },
        ]);
      }
      setStarted(true);
      setChatId(stored.id);
    } else {
      setChat([]);
      setStarted(false);
      setChatId(null);
    }
  }, []);

  const updateHistory = (
    id: number,
    prompt: string,
    reply: string,
    citations: Citation[] = [],
    messages: Message[] = []
  ) => {
    const existing = JSON.parse(localStorage.getItem("betesbot_history") || "[]");
    const index = existing.findIndex((c: any) => c.id === id);

    const updated = {
      id,
      prompt,
      reply,
      citations,
      messages,
      createdAt: new Date().toLocaleString(),
    };

    if (index !== -1) {
      existing[index] = {
        ...existing[index],
        ...updated,
        prompt: existing[index].prompt || prompt,
      };
      localStorage.setItem("betesbot_history", JSON.stringify(existing));
    } else {
      localStorage.setItem(
        "betesbot_history",
        JSON.stringify([updated, ...existing])
      );
    }

    localStorage.setItem("betesbot_active_chat", JSON.stringify(updated));
    window.dispatchEvent(new Event("betesbot-history-updated"));
  };

  const stopRequest = () => {
    abortRef.current?.abort();
    abortRef.current = null;
  };

  const sendMessage = async (custom?: string) => {
    const textToSend = custom ?? input;
    if (!textToSend.trim() || isLoading) return;

    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setStarted(true);

    setChat((prev) => [
      ...prev,
      { role: "user", text: textToSend },
      { role: "assistant", text: "__loading__" },
    ]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          chat_id: chatId,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();

      const newChatId =
        data.chat_id !== undefined ? data.chat_id : chatId;

      if (newChatId !== null && newChatId !== undefined) {
        setChatId(newChatId);
      }

      const rawText =
        data.answer ||
        data.response ||
        data.message ||
        data.reply ||
        "No response returned from server.";

      const cleaned = formatAssistantText(rawText);

      const cites =
        data.citations ||
        data.sources ||
        data.references ||
        [];

      setChat((prev) => {
        const updatedMessages = prev.map((msg, i) =>
          i === prev.length - 1 &&
          msg.role === "assistant" &&
          msg.text === "__loading__"
            ? {
                role: "assistant" as const,
                text: cleaned,
                citations: cites,
              }
            : msg
        );

        if (newChatId !== null && newChatId !== undefined) {
          updateHistory(
            newChatId,
            textToSend,
            cleaned,
            cites,
            updatedMessages
          );
        }

        return updatedMessages;
      });
    } catch (err) {
      const error = err as Error;

      setChat((prev) =>
        prev.map((msg, i) =>
          i === prev.length - 1 &&
          msg.role === "assistant" &&
          msg.text === "__loading__"
            ? { role: "assistant", text: "Error: " + error.message }
            : msg
        )
      );
    } finally {
      abortRef.current = null;
      setIsLoading(false);
      setInput("");
    }
  };

  return (
    <div className="chat-container">
      {!started && <h1 className="page-title">Ask about diabetes!</h1>}

      {!started && (
        <div className="quick-actions">
          {quickPrompts.map((item) => (
            <button
              key={item.title}
              className="quick-action-card"
              onClick={() => sendMessage(item.prompt)}
              disabled={isLoading}
            >
              <div className="quick-action-top">
                <div className="quick-action-icon-wrap">
                  <i className={item.icon}></i>
                </div>
                <div className="quick-action-text">
                  <span className="quick-action-title">{item.title}</span>
                  <span className="quick-action-description">
                    {item.description}
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {started && (
        <div className="chat-thread">
          {chat.map((msg, i) =>
            msg.role === "user" ? (
              <div key={i} className="user-message-row">
                <div className="user-message-bubble">{msg.text}</div>
              </div>
            ) : (
              <div key={i} className="assistant-message-row">
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
                            {msg.citations.map((c, idx) => (
                              <li key={idx}>
                                {typeof c === "string" ? (
                                  c
                                ) : c.url ? (
                                  <a
                                    href={c.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    {c.source ?? c.url}
                                  </a>
                                ) : (
                                  c.source ?? JSON.stringify(c)
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
          started ? "chat-input-after-send" : ""
        }`}
      >
        <input
          type="text"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              if (isLoading) stopRequest();
              else sendMessage();
            }
          }}
          className="chat-input"
        />

        <button
          onClick={isLoading ? stopRequest : () => sendMessage()}
          className="send-btn"
        >
          {isLoading ? (
            <i className="fa-solid fa-square"></i>
          ) : (
            <i className="fa-solid fa-arrow-up"></i>
          )}
        </button>
      </div>

      {!started && (
        <p className="chat-disclaimer">
          For educational use only. This chatbot does not provide professional
          medical advice.
        </p>
      )}
    </div>
  );
};

export default Page1;