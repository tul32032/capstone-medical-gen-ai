import { useEffect, useState } from "react";
import "./Page3.css";
import { API_BASE_URL } from "../constants/constants";

type ChatHistoryItem = {
  id: number;
  prompt: string;
  created_at: string;
};

const Page3 = () => {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);

useEffect(() => {
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/history/`, {
        method: "GET",
        credentials: "include",
      });

      const data = await res.json();

      if (data.error || !data.chats) {
        setHistory([]);
        return;
      }

      setHistory(
        data.chats.map((item: any) => ({
          id: item.id,
          prompt: item.prompt,
          created_at: item.created_at,
        }))
      );
    } catch (err) {
      console.error("failed to fetch history:", err);
    }
  };

  fetchHistory();
}, []);

  const handleExport = async (chat: ChatHistoryItem) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/history/?chat_id=${chat.id}`, {
        credentials: "include",
      });
      if (!res.ok) return;
      
      const data = await res.json();
      const text = `BetesBot Chat Export

Date: ${chat.created_at}

` + data.chat.map((item: any) => 
`Question:
${item.question}

Answer:
${item.answer}

`).join("\n---\n\n");

      const blob = new Blob([text], { type: "text/plain" });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `betesbot-chat-${chat.id}.txt`;
      link.click();

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to export:", err);
    }
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
                <p className="history-date">{chat.created_at}</p>
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