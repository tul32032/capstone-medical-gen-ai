import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Page1 from './pages/Page1';
import Page2 from './pages/Page2';
import Page3 from './pages/Page3';
import './Dashboard.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faUserDoctor,
  faFileLines,
  faClockRotateLeft,
  faCircleUser,
  faArrowRightFromBracket,
} from '@fortawesome/free-solid-svg-icons';

import logo from './assets/BB2.png';

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

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
              <Link to="/dashboard" className="nav-link">
                <FontAwesomeIcon icon={faUserDoctor} className="nav-icon" />
                {!collapsed && <span className="nav-text">New Chat</span>}
              </Link>
            </li>

            <li>
              <Link to="/dashboard/page2" className="nav-link">
                <FontAwesomeIcon icon={faFileLines} className="nav-icon" />
                {!collapsed && <span className="nav-text">Document Library</span>}
              </Link>
            </li>

            <li>
              <Link to="/dashboard/page3" className="nav-link">
                <FontAwesomeIcon icon={faClockRotateLeft} className="nav-icon" />
                {!collapsed && <span className="nav-text">History</span>}
              </Link>
            </li>
          </div>

          {!collapsed && (
            <div className="bottom-section">
              <div className="user-section">
                <div className="user-card">
                  <FontAwesomeIcon icon={faCircleUser} className="nav-icon" />

                  <div className="user-info">
                    <span className="user-name">Your Name</span>
                  </div>

                  <button
                    type="button"
                    className="logout-icon-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate('/');
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
            <Route path="/" element={<Page1 />} />
            <Route path="/page2" element={<Page2 />} />
            <Route path="/page3" element={<Page3 />} />
          </Routes>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;