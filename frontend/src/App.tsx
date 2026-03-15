import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./LoginPage";
import Dashboard from "./Dashboard";
import GoogleCallback from "./GoogleCallback";
import ProtectedRoute from "./ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard/*" element={<Dashboard />} />
        </Route>
        <Route path="/auth/callback" element={<GoogleCallback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App
