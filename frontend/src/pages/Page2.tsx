import { useState } from "react";
import "./Page2.css";

const Page2 = () => {
  const [files, setFiles] = useState<File[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selectedFiles]);
  };

  return (
    <div className="library-container">
      <h1 className="library-title">Document Library</h1>

      <div className="upload-section">
        <label htmlFor="fileUpload" className="upload-box">
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
        {files.length === 0 ? (
          <p className="empty-text">No documents uploaded yet.</p>
        ) : (
          files.map((file, index) => (
            <div key={index} className="file-card">
              <p>{file.name}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Page2;