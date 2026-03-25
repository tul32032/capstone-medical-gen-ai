import { useState } from "react";
import { API_BASE_URL } from "../constants/constants";
import "./Page2.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUpload } from "@fortawesome/free-solid-svg-icons";

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
      const uploadId = `${selectedFile.name}-${selectedFile.size}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

      setFiles((prev) => [
        ...prev,
        {
          id: uploadId,
          name: selectedFile.name,
          status: "uploading",
        },
      ]);

      try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(`${API_BASE_URL}/documents/upload/`, {
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
          accept=".pdf"
          onChange={handleFileChange}
          className="file-input"
        />
      </div>

      <div className="file-grid">
        {files.length === 0 ? (
          <p className="empty-text">No documents uploaded yet.</p>
        ) : (
          files.map((file) => (
            <div key={file.id} className="file-card">
              <p>{file.name}</p>
              <p>Status: {file.status}</p>

              {file.status === "success" && (
                <p style={{ color: "green" }}>
                  Sent to infra ✓{file.infraStatus ? ` (${file.infraStatus})` : ""}
                </p>
              )}

              {file.status === "error" && (
                <p style={{ color: "red" }}>Error: {file.error}</p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Page2;
