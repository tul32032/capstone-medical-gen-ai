import React, { useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"

const GOOGLE_CALLBACK_URL = `${import.meta.env.VITE_API_BASE_URL}/api/auth/login/google/`

const GoogleCallback: React.FC = () => {
  const navigate = useNavigate()
  const fetched = useRef(false)

  useEffect(() => {
    if (fetched.current) return
    fetched.current = true

    const params = new URLSearchParams(window.location.search)
    const code = params.get("code")
    const error = params.get("error")

    if (error || !code) {
      navigate("/")
      return
    }

    fetch(`${GOOGLE_CALLBACK_URL}?code=${encodeURIComponent(code)}`)
      .then((res) => {
        if (!res.ok) throw new Error("Auth failed")
        return res.json()
      })
      .then((data) => {
        localStorage.setItem("access_token", data.access_token)
        localStorage.setItem("refresh_token", data.refresh_token)
        navigate("/dashboard")
      })
      .catch(() => {
        navigate("/")
      })
  }, [navigate])

  return <p>Signing you in...</p>
}

export default GoogleCallback