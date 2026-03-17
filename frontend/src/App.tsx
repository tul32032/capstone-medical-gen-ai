import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./LoginPage";
import Dashboard from "./Dashboard";
import GoogleCallback from "./GoogleCallback";
import ProtectedRoutes from "./ProtectedRoutes";
import { AuthProvider } from "./context/AuthContext";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoutes />}>
            <Route path="/*" element={<Dashboard />} />
          </Route>

          <Route path="/auth/callback" element={<GoogleCallback />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
