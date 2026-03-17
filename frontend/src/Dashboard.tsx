import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Page1 from './pages/Page1';
import Page2 from './pages/Page2';
import Page3 from './pages/Page3';
import './Dashboard.css';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserDoctor, faFileLines, faGear, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from './context/AuthContext';

import logo from './assets/BB2.png';

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
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
          <ul>
            <li>
              <Link to="/" className="nav-link">
                <FontAwesomeIcon icon={faUserDoctor} className="nav-icon" />
                {!collapsed && <span className="nav-text">New Chat</span>}
              </Link>
            </li>

            <li>
              <Link to="/page2" className="nav-link">
                <FontAwesomeIcon icon={faFileLines} className="nav-icon" />
                {!collapsed && <span className="nav-text">Document Library</span>}
              </Link>
            </li>

            <li>
              <Link to="/page3" className="nav-link">
                <FontAwesomeIcon icon={faGear} className="nav-icon" />
                {!collapsed && <span className="nav-text">Page3</span>}
              </Link>
            </li>

            <li>
              <button onClick={handleLogout} type="button">
                <FontAwesomeIcon icon={faRightFromBracket} className="nav-icon" />
                {!collapsed && <span className="nav-text">Logout</span>}
              </button>
            </li>
          </ul>
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
