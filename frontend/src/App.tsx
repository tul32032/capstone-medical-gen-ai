import { BrowserRouter, Routes, Route } from "react-router-dom"
import LoginPage from "./LoginPage"
import SignupPage from "./SignupPage"
import Dashboard from "./Dashboard"
import PrivateRoute from "./PrivateRoute"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route element={<PrivateRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App