import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";

import Page1 from "./pages/Page1";
import Page2 from "./pages/Page2";
import Page3 from "./pages/Page3";
import AdminAnalytics from "./pages/AdminAnalytics";

import "./Dashboard.css";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUserDoctor,
  faFileLines,
  faCircleUser,
  faArrowRightFromBracket,
  faChartLine,
  faTrashCan,
  faDownload,
} from "@fortawesome/free-solid-svg-icons";

import { useAuth } from "./context/AuthContext";
import logo from "./assets/Betesbotlogo.png";

type ChatHistoryItem = {
  id: number;
  prompt: string;
  reply: string;
  createdAt: string;
};

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [activeMenuId, setActiveMenuId] = useState<number | null>(null);

  const menuRef = useRef<HTMLDivElement | null>(null);

  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();

  useEffect(() => {
    const fetchHistory = () => {
      const raw = localStorage.getItem("betesbot_history");
      const parsed = JSON.parse(raw || "[]");

      const valid = parsed.filter(
        (item: ChatHistoryItem) =>
          item &&
          typeof item.prompt === "string" &&
          item.prompt.trim() !== "" &&
          typeof item.reply === "string" &&
          item.reply.trim() !== ""
      );

      setChatHistory(valid);
    };

    fetchHistory();
    window.addEventListener("betesbot-history-updated", fetchHistory);

    return () => {
      window.removeEventListener("betesbot-history-updated", fetchHistory);
    };
  }, []);

  useEffect(() => {
    const closeMenuOnOutsideClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setActiveMenuId(null);
      }
    };

    document.addEventListener("mousedown", closeMenuOnOutsideClick);

    return () => {
      document.removeEventListener("mousedown", closeMenuOnOutsideClick);
    };
  }, []);

  const toggleSidebar = () => {
    setCollapsed((prev) => !prev);
    setActiveMenuId(null);
  };

  const logoutUser = async () => {
    await logout();
    navigate("/login");
  };

  const startNewChat = () => {
    localStorage.removeItem("betesbot_active_chat");
    navigate("/dashboard");
    window.location.reload();
  };

  const openChat = (chat: ChatHistoryItem) => {
    localStorage.setItem("betesbot_active_chat", JSON.stringify(chat));
    navigate("/dashboard");
    window.location.reload();
  };

  const deleteChat = (id: number) => {
    const updatedList = chatHistory.filter((c) => c.id !== id);
    setChatHistory(updatedList);
    localStorage.setItem("betesbot_history", JSON.stringify(updatedList));

    const active = JSON.parse(
      localStorage.getItem("betesbot_active_chat") || "null"
    );

    if (active && active.id === id) {
      localStorage.removeItem("betesbot_active_chat");
    }

    setActiveMenuId(null);
  };

  const exportChat = (chat: ChatHistoryItem) => {
    const fileContent = `BetesBot Chat Export

Date: ${chat.createdAt}

Prompt:
${chat.prompt}

Response:
${chat.reply}`;

    const blob = new Blob([fileContent], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `betesbot-chat-${chat.id}.txt`;
    a.click();

    window.URL.revokeObjectURL(url);
    setActiveMenuId(null);
  };

  const fullName = user
    ? `${user.firstName ?? ""} ${user.lastName ?? ""}`.trim()
    : "Your Name";

  return (
    <div className="dashboard-container">
      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <div className="sidebar-header">
          {!collapsed && (
            <img src={logo} alt="Logo" className="sidebar-logo" />
          )}

          <button
            type="button"
            className="toggle-btn"
            onClick={toggleSidebar}
          >
            {collapsed ? "→" : "←"}
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="top-section">
            <li>
              <button
                type="button"
                className="nav-link nav-button"
                onClick={startNewChat}
              >
                <FontAwesomeIcon icon={faUserDoctor} className="nav-icon" />
                {!collapsed && <span className="nav-text">New Chat</span>}
              </button>
            </li>

            <li>
              <Link to="/dashboard/page2" className="nav-link">
                <FontAwesomeIcon icon={faFileLines} className="nav-icon" />
                {!collapsed && (
                  <span className="nav-text">Document Library</span>
                )}
              </Link>
            </li>

            {isAdmin && (
              <li>
                <Link to="/dashboard/admin" className="nav-link admin-link">
                  <FontAwesomeIcon icon={faChartLine} className="nav-icon" />
                  {!collapsed && (
                    <span className="nav-text">Analytics</span>
                  )}
                </Link>
              </li>
            )}
          </div>

          {!collapsed && chatHistory.length > 0 && (
            <div className="history-sidebar-section">
              <p className="history-sidebar-title">Recent Chats</p>

              <div className="history-sidebar-list">
                {chatHistory.slice(0, 8).map((chat) => (
                  <div
                    key={chat.id}
                    className="history-sidebar-row"
                    ref={activeMenuId === chat.id ? menuRef : null}
                  >
                    <button
                      type="button"
                      className="history-sidebar-item"
                      onClick={() => openChat(chat)}
                    >
                      {chat.prompt}
                    </button>

                    <button
                      type="button"
                      className="chat-menu-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setActiveMenuId(
                          activeMenuId === chat.id ? null : chat.id
                        );
                      }}
                    >
                      ⋯
                    </button>

                    {activeMenuId === chat.id && (
                      <div className="chat-menu-dropdown">
                        <button
                          type="button"
                          className="menu-option"
                          onClick={() => exportChat(chat)}
                        >
                          <FontAwesomeIcon
                            icon={faDownload}
                            style={{ marginRight: "6px" }}
                          />
                          Export
                        </button>

                        <button
                          type="button"
                          className="delete-option"
                          onClick={() => deleteChat(chat.id)}
                        >
                          <FontAwesomeIcon
                            icon={faTrashCan}
                            style={{ marginRight: "6px", color: "red" }}
                          />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bottom-section">
            <div className="user-section">
              <div className="user-card">
                <FontAwesomeIcon icon={faCircleUser} className="nav-icon" />

                {!collapsed && (
                  <div className="user-info">
                    <span className="user-name">{fullName}</span>
                  </div>
                )}

                {!collapsed && (
                  <button
                    type="button"
                    className="logout-icon-btn"
                    onClick={async (e) => {
                      e.stopPropagation();
                      await logoutUser();
                    }}
                  >
                    <FontAwesomeIcon
                      icon={faArrowRightFromBracket}
                      className="logout-icon"
                    />
                  </button>
                )}
              </div>
            </div>
          </div>
        </nav>
      </aside>

      <main className={`main-content ${collapsed ? "expanded" : ""}`}>
        <div className="content-wrapper">
          <Routes>
            <Route index element={<Page1 />} />
            <Route path="page2" element={<Page2 />} />
            <Route path="page3" element={<Page3 />} />
            {isAdmin && <Route path="admin" element={<AdminAnalytics />} />}
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;