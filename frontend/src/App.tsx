import { BrowserRouter, Routes, Route } from "react-router-dom"
import LoginPage from "./LoginPage"
import Dashboard from "./Dashboard"
import GoogleCallback from "./GoogleCallback"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/google" element={<GoogleCallback />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App