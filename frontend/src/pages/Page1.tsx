import { useState } from "react";
import "./Page1.css";
import { AI_INFRA_API } from "../constants/constants";

const Page1 = () => {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setResponse("");
    try {
      const res = await fetch(`${AI_INFRA_API}/api/v1/chat`, {
        method: "POST",
        headers: {
          Authorization:
            "Bearer sk-745bf728a576f712ba3aaa47065273994ade96ee07fc5b734540a1d0e2d32822",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: message,
          project_id: "f660368c-4c8e-4094-acb8-e30fa91e3415",
          system_prompt:
            "You are a endocrinologist with a specialization in diabetes. Your goal is to provide evidence-based information regarding diabetes as well as diabetes management. Every single claim must end with a citation in brackets like [Source: DocName, Page #]. If the source is not in the context, say 'I do not know'.\n\nResponse Structure:\nA brief 1-2 sentence answer.\nA more detailed explanation giving insights derived from the retrieved context.\nA \"References\" section at the bottom.\n\nSafety and Constraints:\nYou cannot prescribe specific dosages for medications. You may discuss standard ranges but must direct the user to their healthcare provider.\nBe professional and clear, avoid overly dense medical jargon unless explaining it.\nStrictly limit your answer to the provided context. Do not use outside knowledge.",
        }),
      });
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
