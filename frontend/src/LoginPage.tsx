import "./LoginPage.css"
import logo from "./assets/BB1.png"
import google from "./assets/google.png"
import { useNavigate } from "react-router-dom"
import React from "react"

const GOOGLE_AUTH_URL =
  "https://accounts.google.com/o/oauth2/v2/auth?" +
  new URLSearchParams({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    redirect_uri: "http://localhost:3000/google",
    response_type: "code",
    scope: "openid email profile",
    access_type: "offline",
    prompt: "select_account",
  }).toString()

const LoginPage: React.FC = () => {
  const navigate = useNavigate()

  const handleLogin = () => {
    navigate("/dashboard")
  }

  const handleGoogleLogin = () => {
    window.location.href = GOOGLE_AUTH_URL
  }

  return (
    <div className="authPage">
      <div className="brand">
        <img className="brandLogo" src={logo} alt="BetesBot logo" />
      </div>

      <div className="authCard">
        <div className="authHeader">
          <h1>Welcome back</h1>
          <p>Enter your credentials to access your account</p>
        </div>

        <form
          className="authForm"
          onSubmit={(e) => {
            e.preventDefault()
            handleLogin()
          }}
        >
          <label className="field">
            <span className="labelText">Email</span>
            <input type="email" placeholder="name@example.com" required />
          </label>

          <div className="rowBetween">
            <span className="labelText">Password</span>
            <button type="button" className="linkBtn">
              Forgot password?
            </button>
          </div>

          <input type="password" required />

          <button className="primaryBtn" type="submit">
            Log in
          </button>

          <div className="dividerRow">
            <span className="line" />
            <span className="dividerText">OR CONTINUE WITH</span>
            <span className="line" />
          </div>

          <button className="googleBtn" type="button" onClick={handleGoogleLogin}>
            <span className="googleIcon" aria-hidden="true">
              <img src={google} alt="Google logo" className="google-icon" />
            </span>
            <span>Google</span>
          </button>

          <div className="footerText">
            Don&apos;t have an account?{" "}
            <button type="button" className="linkBtn">
              Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
