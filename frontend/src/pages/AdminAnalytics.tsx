import { useState, useEffect } from "react";
import "./AdminAnalytics.css";
import { API_BASE_URL } from "../constants/constants";

type Document = {
  id: string;
  team_id: string;
  project_id: string;
  title: string;
  source_type: string;
  gcs_uri: string;
  status: string;
};

type AnalyticsData = {
  total_queries: number;
  total_documents: number;
  total_users: number;
  documents: Document[];
  total_cost: number;
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
          const data = await res.json().catch(() => ({}));
          if (data.error) {
            throw new Error(data.error);
          }
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
    },
    {
      title: "Documents Uploaded",
      value: data.total_documents,
      icon: "📄",
    },
    {
      title: "Total Users",
      value: data.total_users,
      icon: "👥",
    },
    {
      title: "Total Cost",
      value:
        typeof data.total_cost === "number"
          ? `$${data.total_cost.toFixed(2)}`
          : data.total_cost,
      icon: "💰",
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
              <div className="stat-icon">
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
        <h2 className="section-title">Uploaded Documents</h2>
        <div className="documents-list">
          {data.documents && data.documents.length > 0 ? (
            data.documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="document-icon">📄</div>
                <div className="document-info">
                  <span className="document-name">{doc.title}</span>
                  <span className="document-date">{doc.source_type}</span>
                </div>
                <span className={`document-status ${doc.status}`}>
                  {doc.status}
                </span>
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
