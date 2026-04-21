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
    icon: "fa-solid fa-stethoscope"
  },
  {
    title: "Blood Sugar Guide",
    description: "View normal ranges and what your levels may mean",
    prompt: "What are normal blood sugar ranges?",
    icon: "fa-solid fa-chart-column"
  },
  {
    title: "Diet Recommendations",
    description: "Get food suggestions and meal guidance for diabetes?",
    prompt: "What foods are recommended for someone with diabetes?",
    icon: "fa-solid fa-bowl-food"
  },
  {
    title: "Title Later",
    description: "Paragraph later",
    prompt: "Give me general diabetes management advice.",
    icon: "fa-solid fa-clipboard-check"
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
  const [activeChatId, setActiveChatId] = useState<number | null>(null);

  useEffect(() => {
    const activeChat = JSON.parse(
      localStorage.getItem("betesbot_active_chat") || "null"
    );

    if (activeChat) {
      if (activeChat.messages) {
        setMessages(activeChat.messages);
      } else {
        setMessages([
          { role: "user", text: activeChat.prompt },
          {
            role: "assistant",
            text: activeChat.reply,
            citations: activeChat.citations || []
          }
        ]);
      }
      setHasStartedChat(true);
      setActiveChatId(activeChat.id);
    } else {
      setMessages([]);
      setHasStartedChat(false);
      setActiveChatId(null);
    }
  }, []);

  const saveChatToHistory = (
    chatId: number,
    prompt: string,
    reply: string,
    citations: Citation[] = [],
    allMessages: Message[] = []
  ) => {
    const existing = JSON.parse(localStorage.getItem("betesbot_history") || "[]");

    const existingIndex = existing.findIndex((chat: any) => chat.id === chatId);

    if (existingIndex !== -1) {
      const updatedChat = {
        ...existing[existingIndex],
        prompt: existing[existingIndex].prompt || prompt,
        reply,
        citations,
        messages: allMessages,
        createdAt: new Date().toLocaleString(),
      };

      existing[existingIndex] = updatedChat;
      localStorage.setItem("betesbot_history", JSON.stringify(existing));
      localStorage.setItem("betesbot_active_chat", JSON.stringify(updatedChat));
    } else {
      const newChat = {
        id: chatId,
        prompt,
        reply,
        citations,
        messages: allMessages,
        createdAt: new Date().toLocaleString(),
      };

      localStorage.setItem(
        "betesbot_history",
        JSON.stringify([newChat, ...existing])
      );

      localStorage.setItem("betesbot_active_chat", JSON.stringify(newChat));
    }

    window.dispatchEvent(new Event("betesbot-history-updated"));
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
        body: JSON.stringify({
          message: finalMessage,
          chat_id: activeChatId
        }),
        signal: abortController.signal,
      });

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }

      const data = await res.json();

      const currentChatId =
        data.chat_id !== undefined ? data.chat_id : activeChatId;

      if (currentChatId !== null && currentChatId !== undefined) {
        setActiveChatId(currentChatId);
      }

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

      setMessages((prev) => {
        const updatedMessages = prev.map((msg, index) =>
          index === prev.length - 1 &&
          msg.role === "assistant" &&
          msg.text === "__loading__"
            ? {
                role: "assistant" as const,
                text: assistantText,
                citations: assistantCitations
              }
            : msg
        );

        if (currentChatId !== null && currentChatId !== undefined) {
          saveChatToHistory(
            currentChatId,
            finalMessage,
            assistantText,
            assistantCitations,
            updatedMessages
          );
        }

        return updatedMessages;
      });

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

      <div className={`chat-input-container ${hasStartedChat ? "chat-input-after-send" : ""}`}>
        <input
          type="text"
          placeholder="Type your question..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              if (loading) handleStop();
              else handleSend();
            }
          }}
          className="chat-input"
        />

        <button
          onClick={loading ? handleStop : () => handleSend()}
          className="send-btn"
        >
          {loading ? <i className="fa-solid fa-square"></i> : <i className="fa-solid fa-arrow-up"></i>}
        </button>
      </div>

      {!hasStartedChat && (
        <p className="chat-disclaimer">
          For educational use only. This chatbot does not provide professional medical advice.
        </p>
      )}
    </div>
  );
};

export default Page1;