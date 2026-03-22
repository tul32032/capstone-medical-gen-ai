import { useEffect, useState } from "react";
import "./Page3.css";

type ChatHistoryItem = {
  id: number;
  prompt: string;
  reply: string;
  createdAt: string;
};

const Page3 = () => {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);

  useEffect(() => {
    // TEMP: loading chat history from localStorage (replace with backend fetch later)
    const saved = JSON.parse(localStorage.getItem("betesbot_history") || "[]");
    setHistory(saved);
  }, []);

  const handleExport = (chat: ChatHistoryItem) => {
    const text = `BetesBot Chat Export

Date: ${chat.createdAt}

Prompt:
${chat.prompt}

Response:
${chat.reply}`;

    const blob = new Blob([text], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `betesbot-chat-${chat.id}.txt`;
    link.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="history-container">
      <h1 className="history-title">History</h1>

      {history.length === 0 ? (
        <p className="empty-text">No chats yet.</p>
      ) : (
        history.map((chat) => (
          <div key={chat.id} className="history-card">
            <div className="history-card-header">
              <div>
                <h3 className="history-prompt">{chat.prompt}</h3>
                <p className="history-date">{chat.createdAt}</p>
              </div>

              <button
                onClick={() => handleExport(chat)}
                className="export-btn"
              >
                Export as PDF
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default Page3;