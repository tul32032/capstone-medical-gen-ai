import { createContext, useContext, useState, useEffect } from "react";
import type { AuthUser } from "../types/AuthUser";
import { API_BASE_URL } from "../constants/constants";


type AuthContextType = {
 user: AuthUser | null;
 setUser: (user: AuthUser | null) => void;
 isAdmin: boolean;
 setIsAdmin: (isAdmin: boolean) => void;
 loading: boolean;
 logout: () => Promise<void>;
};


const AuthContext = createContext<AuthContextType | null>(null);


export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
 const [loading, setLoading] = useState(true);


  const logout = async () => {
    await fetch(`${API_BASE_URL}/api/auth/logout/`, {
      method: "POST",
      credentials: "include",
    });
    setUser(null);
    setIsAdmin(false);
  };


 useEffect(() => {
   fetch(`${API_BASE_URL}/api/auth/me/`, {
     credentials: "include",
   })
     .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) {
          setUser({
            id: data.user.id,
            firstName: data.user.first_name,
            lastName: data.user.last_name,
            email: data.user.email,
            isAdmin: data.user.is_superuser || false,
          });
          setIsAdmin(data.user.is_superuser || false);
        }
      })
     .finally(() => setLoading(false));
 }, []);


  return (
    <AuthContext.Provider value={{ user, setUser, isAdmin, setIsAdmin, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth(): AuthContextType {
 const ctx = useContext(AuthContext);
 if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
 return ctx;
}
