import "./LoginPage.css";
import logo from "./assets/BB1.png";
import google from "./assets/google.png";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import React from "react";

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("/api/signup/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        setError(data.detail ?? "Signup failed. Please try again.");
        return;
      }

      navigate("/dashboard");
    } catch {
      setError("Signup failed. Please try again.");
    }
  };

  return (
    <div className="authPage">
      <div className="brand">
        <img className="brandLogo" src={logo} alt="BetesBot logo" />
      </div>

      <div className="authCard">
        <div className="authHeader">
          <h1>Create an account</h1>
          <p>Enter your email and password to get started</p>
        </div>

        <form className="authForm" onSubmit={handleSignup}>
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
            <span className="labelText">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && <p className="errorText">{error}</p>}

          <button className="primaryBtn" type="submit">
            Sign up
          </button>

          <div className="dividerRow">
            <span className="line" />
            <span className="dividerText">OR CONTINUE WITH</span>
            <span className="line" />
          </div>

          <button className="googleBtn" type="button">
            <span className="googleIcon" aria-hidden="true">
              <img src={google} alt="Google logo" className="google-icon" />
            </span>
            <span>Google</span>
          </button>

          <div className="footerText">
            Already have an account?{" "}
            <button
              type="button"
              className="linkBtn"
              onClick={() => navigate("/")}
            >
              Log in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;
