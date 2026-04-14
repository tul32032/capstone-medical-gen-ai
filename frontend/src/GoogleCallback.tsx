import React, { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { API_BASE_URL } from "./constants/constants";

const GoogleCallback: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setIsAdmin } = useAuth();
  const fetched = useRef(false);

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;

    const handleCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const error = params.get("error");

      if (error || !code) {
        navigate("/login", { replace: true });
        return;
      }

      try {
        const res = await fetch(
          `${API_BASE_URL}/api/auth/login/google/`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ code }),
          },
        );

        if (!res.ok) throw new Error("Auth failed");

        const data = await res.json();
        setUser({
          id: data.user.id,
          firstName: data.user.first_name,
          lastName: data.user.last_name,
          email: data.user.email,
          isAdmin: data.user.is_superuser || false,
        });
        setIsAdmin(data.user.is_superuser || false);
        navigate("/", { replace: true });
      } catch {
        navigate("/login", { replace: true });
      }
    };

    handleCallback();
  }, [navigate, setUser, setIsAdmin]);

  return <div>Signing you in...</div>;
};

export default GoogleCallback;
