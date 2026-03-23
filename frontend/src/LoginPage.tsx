import "./LoginPage.css";
import logo from "./assets/BB1.png";
import google from "./assets/google.png";
import { useNavigate } from "react-router-dom";
import React, { useState } from "react";
import { GOOGLE_CLIENT_ID, GOOGLE_CALLBACK, API_BASE_URL } from "./constants/constants";
import { useAuth } from "./context/AuthContext";

const GOOGLE_AUTH_URL =
  "https://accounts.google.com/o/oauth2/v2/auth?" +
  new URLSearchParams({
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: GOOGLE_CALLBACK,
    response_type: "code",
    scope: "email profile",
    access_type: "offline",
    prompt: "consent",
  }).toString();

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGoogleLogin = () => {
    window.location.href = GOOGLE_AUTH_URL;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const isSignup = mode === "signup";
    const url = isSignup
      ? `${API_BASE_URL}/api/auth/signup/email/`
      : `${API_BASE_URL}/api/auth/login/email/`;

    const body: Record<string, string> = { email, password };
    if (isSignup) {
      body.first_name = firstName;
      body.last_name = lastName;
    }

    try {
      const res = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? "Something went wrong. Please try again.");
        return;
      }

      setUser({
        id: data.user.id,
        firstName: data.user.first_name,
        lastName: data.user.last_name,
        email: data.user.email,
      });
      navigate("/dashboard");
    } catch {
      setError("Network error. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode((m) => (m === "login" ? "signup" : "login"));
    setError("");
  };

  return (
    <div className="authPage">
      <div className="brand">
        <img className="brandLogo" src={logo} alt="BetesBot logo" />
      </div>

      <div className="authCard">
        <div className="authHeader">
          <h1>{mode === "login" ? "Welcome back" : "Create account"}</h1>
          <p>
            {mode === "login"
              ? "Enter your credentials to access your account"
              : "Sign up to get started"}
          </p>
        </div>

        <form className="authForm" onSubmit={handleSubmit}>
          {mode === "signup" && (
            <div className="rowHalf">
              <label className="field">
                <span className="labelText">First name</span>
                <input
                  type="text"
                  placeholder="Jane"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                />
              </label>
              <label className="field">
                <span className="labelText">Last name</span>
                <input
                  type="text"
                  placeholder="Doe"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                />
              </label>
            </div>
          )}

          <label className="field">
            <span className="labelText">Email</span>
            <input
              type="email"
              placeholder="name@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="field">
            <div className="rowBetween">
              <span className="labelText">Password</span>
              {mode === "login" && (
                <button type="button" className="linkBtn">
                  Forgot password?
                </button>
              )}
            </div>
            <input
              type="password"
              required
              minLength={mode === "signup" ? 8 : undefined}
              placeholder={mode === "signup" ? "At least 8 characters" : ""}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && <p className="errorText">{error}</p>}

          <button className="primaryBtn" type="submit" disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Log in" : "Sign up"}
          </button>

          <div className="dividerRow">
            <span className="line" />
            <span className="dividerText">OR CONTINUE WITH</span>
            <span className="line" />
          </div>

          <button
            className="googleBtn"
            type="button"
            onClick={handleGoogleLogin}
          >
            <span className="googleIcon" aria-hidden="true">
              <img src={google} alt="Google logo" className="google-icon" />
            </span>
            <span>Google</span>
          </button>

          <div className="footerText">
            {mode === "login" ? (
              <>
                Don&apos;t have an account?{" "}
                <button type="button" className="linkBtn" onClick={switchMode}>
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button type="button" className="linkBtn" onClick={switchMode}>
                  Log in
                </button>
              </>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
