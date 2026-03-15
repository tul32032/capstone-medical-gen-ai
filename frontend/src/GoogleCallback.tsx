import React, { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const GoogleCallback: React.FC = () => {
  const navigate = useNavigate();
  const fetched = useRef(false);

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;

    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const error = params.get("error");

      if (error || !code) {
        navigate("/", { replace: true });
        return;
      }

      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/auth/login/google/`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ code }),
          },
        );

        if (!res.ok) throw new Error("Auth failed");

        navigate("/dashboard", { replace: true });
      } catch {
        navigate("/", { replace: true });
      }
    };

    handleCallback();
  }, [navigate]);

  return <div>Signing you in...</div>;
};

export default GoogleCallback;
