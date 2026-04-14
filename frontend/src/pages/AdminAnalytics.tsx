import { useState, useEffect } from "react";
import "./AdminAnalytics.css";
import { API_BASE_URL } from "../constants/constants";

type Document = {
  id: string;
  name: string;
  uploaded_at: string;
  status?: string;
};

type AnalyticsData = {
  total_queries: number;
  total_documents: number;
  total_users: number;
  recent_queries: number;
  documents: Document[];
};

const AdminAnalytics = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/analytics/admin/`, {
          credentials: "include",
        });
        
        if (!res.ok) {
          if (res.status === 403) {
            throw new Error("Admin access required");
          }
          throw new Error("Failed to fetch analytics");
        }
        
        const result = await res.json();
        setData(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="analytics-loading">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="analytics-error">{error}</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const statCards = [
    {
      title: "Total Queries",
      value: data.total_queries,
      icon: "💬",
      color: "#4770c1",
    },
    {
      title: "Documents Uploaded",
      value: data.total_documents,
      icon: "📄",
      color: "#22c55e",
    },
    {
      title: "Total Users",
      value: data.total_users,
      icon: "👥",
      color: "#f59e0b",
    },
  ];

  const recentCards = [
    {
      title: "Queries (Last 7 Days)",
      value: data.recent_queries,
      icon: "📈",
      color: "#8b5cf6",
    },
  ];

  return (
    <div className="analytics-container">
      <h1 className="analytics-title">Admin Analytics Dashboard</h1>

      <section className="analytics-section">
        <h2 className="section-title">Overview</h2>
        <div className="stats-grid">
          {statCards.map((card) => (
            <div key={card.title} className="stat-card">
              <div className="stat-icon" style={{ backgroundColor: `${card.color}15` }}>
                <span style={{ fontSize: "24px" }}>{card.icon}</span>
              </div>
              <div className="stat-info">
                <span className="stat-value">{card.value}</span>
                <span className="stat-title">{card.title}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="analytics-section">
        <h2 className="section-title">Recent Activity (Last 7 Days)</h2>
        <div className="stats-grid small">
          {recentCards.map((card) => (
            <div key={card.title} className="stat-card small">
              <div className="stat-icon" style={{ backgroundColor: `${card.color}15` }}>
                <span style={{ fontSize: "20px" }}>{card.icon}</span>
              </div>
              <div className="stat-info">
                <span className="stat-value">{card.value}</span>
                <span className="stat-title">{card.title}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="analytics-section">
        <h2 className="section-title">Uploaded Documents</h2>
        <div className="documents-list">
          {data.documents && data.documents.length > 0 ? (
            data.documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="document-icon">📄</div>
                <div className="document-info">
                  <span className="document-name">{doc.name}</span>
                  <span className="document-date">
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </span>
                </div>
                {doc.status && (
                  <span className={`document-status ${doc.status}`}>
                    {doc.status}
                  </span>
                )}
              </div>
            ))
          ) : (
            <p className="no-data">No documents uploaded yet</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default AdminAnalytics;
