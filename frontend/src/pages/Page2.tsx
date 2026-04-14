import { useState } from "react";
import { API_BASE_URL } from "../constants/constants";
import "./Page2.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUpload,
  faFileLines,
  faCircleCheck,
  faCircleExclamation,
  faSpinner,
} from "@fortawesome/free-solid-svg-icons";

type UploadedDoc = {
  id: string;
  name: string;
  status: "uploading" | "success" | "error";
  error?: string;
  infraStatus?: number;
  infraSuccess?: boolean;
};

const Page2 = () => {
  const [files, setFiles] = useState<UploadedDoc[]>([]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);

    for (const selectedFile of selectedFiles) {
      const uploadId = `${selectedFile.name}-${selectedFile.size}-${Date.now()}-${Math.random()
        .toString(36)
        .slice(2, 8)}`;

      setFiles((prev) => [
        {
          id: uploadId,
          name: selectedFile.name,
          status: "uploading",
        },
        ...prev,
      ]);

      try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(`${API_BASE_URL}/api/upload/`, {
          method: "POST",
          credentials: "include",
          body: formData,
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
          ? await response.json()
          : { error: await response.text() };

        if (!response.ok || data.success === false) {
          throw new Error(
            data.infra_error ||
              data.error ||
              data.detail ||
              `Upload failed${data.status ? ` (${data.status})` : "."}`
          );
        }

        setFiles((prev) =>
          prev.map((file) =>
            file.id === uploadId
              ? {
                  ...file,
                  status: "success",
                  infraStatus: data.status,
                  infraSuccess: data.success,
                }
              : file
          )
        );
      } catch (error) {
        const message = error instanceof Error ? error.message : "Upload failed.";

        setFiles((prev) =>
          prev.map((file) =>
            file.id === uploadId
              ? {
                  ...file,
                  status: "error",
                  error: message,
                }
              : file
          )
        );
      }
    }

    e.target.value = "";
  };

  const recentUploads = files;

  return (
    <div className="library-container">
      <div className="library-header">
        <h1 className="library-title">Document Library</h1>
        <p className="library-subtitle">
          Upload medical documents to provide context for AI-generated responses
        </p>
      </div>

      <div className="library-content">
        <div className="upload-panel">
          <label htmlFor="fileUpload" className="upload-box">
            <FontAwesomeIcon icon={faUpload} className="upload-main-icon" />
            <p className="upload-heading">Drag & drop files here</p>
            <span className="upload-button">Upload Documents</span>
            <p className="upload-support-text">Supports PDF and TXT files</p>
          </label>

          <input
            id="fileUpload"
            type="file"
            multiple
            accept=".pdf,application/pdf,.txt"
            onChange={handleFileChange}
            className="file-input"
          />
        </div>

        <div className="files-panel">
          <div className="files-panel-header">
            <h2>Uploaded Files</h2>
          </div>

          {files.length === 0 ? (
            <div className="empty-state">
              <p className="empty-text">No documents uploaded yet.</p>
            </div>
          ) : (
            <div className="file-grid">
              {files.slice(0, 1).map((file) => (
                <div
                  key={file.id}
                  className={`file-card ${
                    file.status === "success"
                      ? "file-card--success"
                      : file.status === "error"
                      ? "file-card--error"
                      : ""
                  }`}
                >
                  <FontAwesomeIcon icon={faFileLines} className="file-card__icon" />

                  <p className="file-card__name">{file.name}</p>

                  <div className="file-card__status">
                    {file.status === "uploading" && (
                      <>
                        <FontAwesomeIcon
                          icon={faSpinner}
                          spin
                          className="status-icon status-icon--uploading"
                        />
                        <span>Uploading...</span>
                      </>
                    )}

                    {file.status === "success" && (
                      <>
                        <FontAwesomeIcon
                          icon={faCircleCheck}
                          className="status-icon status-icon--success"
                        />
                        <span>Uploaded successfully</span>
                      </>
                    )}

                    {file.status === "error" && (
                      <>
                        <FontAwesomeIcon
                          icon={faCircleExclamation}
                          className="status-icon status-icon--error"
                        />
                        <span>Upload failed</span>
                        <span className="status-error-msg">{file.error}</span>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="recent-uploads-section">
        <div className="recent-uploads-header">
          <h2>Recent Uploads</h2>
        </div>

        {recentUploads.length === 0 ? (
          <div className="recent-uploads-empty">
            <p>No recent uploads yet.</p>
          </div>
        ) : (
          <div className="recent-uploads-table">
            <div className="recent-uploads-table-head">
              <span>Name</span>
              <span>Status</span>
              <span>Type</span>
            </div>

            {recentUploads.map((file) => {
              const fileType = file.name.toLowerCase().endsWith(".pdf") ? "PDF" : "TXT";

              return (
                <div key={file.id} className="recent-upload-row">
                  <div className="recent-upload-name">
                    <FontAwesomeIcon icon={faFileLines} className="recent-upload-file-icon" />
                    <span>{file.name}</span>
                  </div>

                  <div className="recent-upload-status">
                    <span
                      className={`recent-status-pill ${
                        file.status === "success"
                          ? "recent-status-pill--success"
                          : file.status === "error"
                          ? "recent-status-pill--error"
                          : "recent-status-pill--uploading"
                      }`}
                    >
                      {file.status === "success"
                        ? "Uploaded"
                        : file.status === "error"
                        ? "Failed"
                        : "Uploading"}
                    </span>
                  </div>

                  <div className="recent-upload-type">{fileType}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Page2;