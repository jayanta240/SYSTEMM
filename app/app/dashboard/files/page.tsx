"use client";

import { useEffect, useState } from "react";

type FileItem = {
  id: number;
  filename: string;
  filetype: string;
  cloudinary_url: string;
  size_mb: number;
  uploaded_at: string;
};

export default function FilesPage() {

  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {

      const res = await fetch(
        "http://127.0.0.1:8000/api/files"
      );

      const data = await res.json();

      setFiles(data);

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f172a",
        color: "white",
        padding: "30px"
      }}
    >

      <h1
        style={{
          fontSize: "32px",
          fontWeight: "bold",
          marginBottom: "30px"
        }}
      >
        📁 File Management
      </h1>

      {loading ? (
        <p>Loading files...</p>
      ) : files.length === 0 ? (
        <p>No uploaded files found.</p>
      ) : (

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "20px"
          }}
        >

          {files.map((file) => (

            <div
              key={file.id}
              style={{
                background: "#1e293b",
                padding: "20px",
                borderRadius: "14px",
                border: "1px solid #334155"
              }}
            >

              <h2
                style={{
                  fontSize: "18px",
                  marginBottom: "12px",
                  wordBreak: "break-word"
                }}
              >
                🎥 {file.filename}
              </h2>

              <p>
                <strong>Type:</strong> {file.filetype}
              </p>

              <p>
                <strong>Size:</strong> {file.size_mb} MB
              </p>

              <p>
                <strong>Uploaded:</strong>
                <br />
                {file.uploaded_at}
              </p>

              <video
                controls
                width="100%"
                style={{
                  marginTop: "15px",
                  borderRadius: "10px"
                }}
              >
                <source
                  src={file.cloudinary_url}
                  type="video/mp4"
                />
              </video>
              <button
                 onClick={async () => {

                   const confirmDelete = confirm(
                     "Delete this file?"
                   );

                   if (!confirmDelete) return;

                   await fetch(
                     `http://127.0.0.1:8000/api/files/${file.id}`,
                     {
                       method: "DELETE"
                     }
                   );

                   fetchFiles();
                 }}
                 style={{
                   marginTop: "15px",
                   width: "100%",
                   padding: "10px",
                   background: "#ef4444",
                   border: "none",
                   borderRadius: "8px",
                   color: "white",
                   cursor: "pointer"
                 }}
               >
                 Delete File
               </button>

            </div>

          ))}

        </div>
      )}
    </div>
  );
}