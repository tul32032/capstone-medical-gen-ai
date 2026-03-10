import { useEffect, useState } from "react"
import { Navigate, Outlet } from "react-router-dom"

type AuthState = "loading" | "authenticated" | "unauthenticated"

async function checkAuth(): Promise<boolean> {
  const res = await fetch("/api/test/", { credentials: "include" })
  if (res.ok) {
    const data = await res.json()
    return data.success === true
  }

  if (res.status === 401) {
    const refreshRes = await fetch("/api/token/refresh/", {
      method: "POST",
      credentials: "include",
    })
    if (refreshRes.ok) {
      const refreshData = await refreshRes.json()
      return refreshData.success === true
    }
  }

  return false
}

export default function PrivateRoute() {
  const [authState, setAuthState] = useState<AuthState>("loading")

  useEffect(() => {
    checkAuth()
      .then((ok) => setAuthState(ok ? "authenticated" : "unauthenticated"))
      .catch(() => setAuthState("unauthenticated"))
  }, [])

  if (authState === "loading") return null
  if (authState === "unauthenticated") return <Navigate to="/" replace />
  return <Outlet />
}
