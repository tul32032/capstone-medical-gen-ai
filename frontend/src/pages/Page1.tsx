import { useState } from "react";
import './Page1.css'

const Page1 = () => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (!message.trim()) return;

    console.log("User message:", message);
    setMessage("");
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

        <button onClick={handleSend} className="send-btn">
          Send
        </button>
      </div>
    </div>
  );
};

export default Page1;