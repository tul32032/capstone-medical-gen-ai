import { useState } from "react";
import './Page1.css'
import { API_BASE_URL } from "../constants/constants";

const Page1 = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setResponse("");
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/?message=${encodeURIComponent(message)}`);
      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch (err) {
      setResponse("Error: " + (err as Error).message);
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  return (
    <div className="chat-container">
      <h1 className="page-title">Ask about diabetes!</h1>

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

        <button onClick={handleSend} className="send-btn" disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </div>

      {response && (
        <div className="response-container">
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
};

export default Page1;
