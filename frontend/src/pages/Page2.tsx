import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileLines, faUpload, faCircleCheck, faCircleXmark, faSpinner } from "@fortawesome/free-solid-svg-icons";
import { API_BASE_URL } from "../constants/constants";
import "./Page2.css";

type UploadedFile = {
  name: string;
  status: "uploading" | "success" | "error";
  errorMsg?: string;
};

const Page2 = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);
    e.target.value = "";

    for (const file of selectedFiles) {
      setUploadedFiles((prev) => [...prev, { name: file.name, status: "uploading" }]);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await fetch(`${API_BASE_URL}/api/upload/`, {
          method: "POST",
          credentials: "include",
          body: formData,
        });

        if (response.ok) {
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.name === file.name && f.status === "uploading"
                ? { ...f, status: "success" }
                : f
            )
          );
        } else {
          const data = await response.json().catch(() => ({}));
          setUploadedFiles((prev) =>
            prev.map((f) =>
              f.name === file.name && f.status === "uploading"
                ? { ...f, status: "error", errorMsg: data.error ?? "Upload failed" }
                : f
            )
          );
        }
      } catch {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.name === file.name && f.status === "uploading"
              ? { ...f, status: "error", errorMsg: "Network error" }
              : f
          )
        );
      }
    }
  };

  return (
    <div className="library-container">
      <h1 className="library-title">Document Library</h1>

      <div className="upload-section">
        <label htmlFor="fileUpload" className="upload-box">
          <FontAwesomeIcon icon={faUpload} className="upload-icon" />
          Click here to upload files
        </label>
        <input
          id="fileUpload"
          type="file"
          multiple
          onChange={handleFileChange}
          className="file-input"
        />
      </div>

      <div className="file-grid">
        {uploadedFiles.length === 0 ? (
          <p className="empty-text">No documents uploaded yet.</p>
        ) : (
          uploadedFiles.map((file, index) => (
            <div key={index} className={`file-card file-card--${file.status}`}>
              <FontAwesomeIcon icon={faFileLines} className="file-card__icon" />
              <p className="file-card__name">{file.name}</p>
              <div className="file-card__status">
                {file.status === "uploading" && (
                  <FontAwesomeIcon icon={faSpinner} spin className="status-icon status-icon--uploading" />
                )}
                {file.status === "success" && (
                  <FontAwesomeIcon icon={faCircleCheck} className="status-icon status-icon--success" />
                )}
                {file.status === "error" && (
                  <>
                    <FontAwesomeIcon icon={faCircleXmark} className="status-icon status-icon--error" />
                    {file.errorMsg && <span className="status-error-msg">{file.errorMsg}</span>}
                  </>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Page2;
