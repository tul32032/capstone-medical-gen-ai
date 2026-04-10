import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Page1 from './pages/Page1';
import Page2 from './pages/Page2';
import Page3 from './pages/Page3';
import AdminAnalytics from './pages/AdminAnalytics';
import './Dashboard.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faUserDoctor,
  faFileLines,
  faCircleUser,
  faArrowRightFromBracket,
  faChartLine,
} from '@fortawesome/free-solid-svg-icons';

import { useAuth } from './context/AuthContext';
import logo from './assets/BB2.png';

type ChatHistoryItem = {
  id: number;
  prompt: string;
  reply: string;
  createdAt: string;
};

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("betesbot_history") || "[]");

    const cleanedHistory = saved.filter(
      (chat: ChatHistoryItem) =>
        chat &&
        typeof chat.prompt === "string" &&
        chat.prompt.trim() !== "" &&
        typeof chat.reply === "string" &&
        chat.reply.trim() !== ""
    );

    setHistory(cleanedHistory);
  }, []);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleNewChat = () => {
    localStorage.removeItem("betesbot_active_chat");
    navigate('/dashboard');
    window.location.reload();
  };

  const handleOpenChat = (chat: ChatHistoryItem) => {
    localStorage.setItem("betesbot_active_chat", JSON.stringify(chat));
    navigate('/dashboard');
    window.location.reload();
  };

  const handleDelete = (chatId: number) => {
    const updated = history.filter((chat) => chat.id !== chatId);
    setHistory(updated);
    localStorage.setItem("betesbot_history", JSON.stringify(updated));

    const activeChat = JSON.parse(
      localStorage.getItem("betesbot_active_chat") || "null"
    );

    if (activeChat && activeChat.id === chatId) {
      localStorage.removeItem("betesbot_active_chat");
    }

    setOpenMenuId(null);
  };

  const handleExport = (chat: ChatHistoryItem) => {
    const text = `BetesBot Chat Export

Date: ${chat.createdAt}

Prompt:
${chat.prompt}

Response:
${chat.reply}`;

    const blob = new Blob([text], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `betesbot-chat-${chat.id}.txt`;
    link.click();

    window.URL.revokeObjectURL(url);
    setOpenMenuId(null);
  };

  const fullName =
    user ? `${user.firstName ?? ''} ${user.lastName ?? ''}`.trim() : 'Your Name';

  return (
    <div className="dashboard-container">
      <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          {!collapsed && <img src={logo} alt="Logo" className="sidebar-logo" />}

          <button onClick={toggleSidebar} className="toggle-btn" type="button">
            {collapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="top-section">
            <li>
              <button
                type="button"
                className="nav-link nav-button"
                onClick={handleNewChat}
              >
                <FontAwesomeIcon icon={faUserDoctor} className="nav-icon" />
                {!collapsed && <span className="nav-text">New Chat</span>}
              </button>
            </li>

            <li>
              <Link to="/dashboard/page2" className="nav-link">
                <FontAwesomeIcon icon={faFileLines} className="nav-icon" />
                {!collapsed && <span className="nav-text">Document Library</span>}
              </Link>
            </li>


            {isAdmin && (
              <li>
                <Link to="/dashboard/admin" className="nav-link admin-link">
                  <FontAwesomeIcon icon={faChartLine} className="nav-icon" />
                  {!collapsed && <span className="nav-text">Analytics</span>}
                </Link>
              </li>
            )}
          </div>

          {!collapsed && history.length > 0 && (
            <div className="history-sidebar-section">
              <p className="history-sidebar-title">Recent Chats</p>

              <div className="history-sidebar-list">
                {history.slice(0, 8).map((chat) => (
                  <div key={chat.id} className="history-sidebar-row">
                    <button
                      type="button"
                      className="history-sidebar-item"
                      onClick={() => handleOpenChat(chat)}
                    >
                      {chat.prompt}
                    </button>

                    <button
                      type="button"
                      className="chat-menu-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(openMenuId === chat.id ? null : chat.id);
                      }}
                    >
                      ⋯
                    </button>

                    {openMenuId === chat.id && (
                      <div className="chat-menu-dropdown">
                        <button
                          type="button"
                          onClick={() => handleExport(chat)}
                        >
                          Export
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDelete(chat.id)}
                          className="delete-option"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {!collapsed && (
            <div className="bottom-section">
              <div className="user-section">
                <div className="user-card">
                  <FontAwesomeIcon icon={faCircleUser} className="nav-icon" />

                  <div className="user-info">
                    <span className="user-name">{fullName}</span>
                  </div>

                  <button
                    type="button"
                    className="logout-icon-btn"
                    onClick={async (e) => {
                      e.stopPropagation();
                      await handleLogout();
                    }}
                  >
                    <FontAwesomeIcon
                      icon={faArrowRightFromBracket}
                      className="logout-icon"
                    />
                  </button>
                </div>
              </div>
            </div>
          )}
        </nav>
      </aside>

      <main className={`main-content ${collapsed ? 'expanded' : ''}`}>
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
