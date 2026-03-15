import React, { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";

type AuthState = "loading" | "authenticated" | "unauthenticated";

const ProtectedRoute: React.FC = () => {
  const [authState, setAuthState] = useState<AuthState>("loading");

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/api/auth/me/`,
          { credentials: "include" }
        );
        console.log(res)
        setAuthState(res.ok ? "authenticated" : "unauthenticated");
      } catch {
        setAuthState("unauthenticated");
      }
    };

    checkAuth();
  }, []);

  if (authState === "loading") return null;
  if (authState === "unauthenticated") return <Navigate to="/" replace />;
  return <Outlet />;
};

export default ProtectedRoute;
