"use client";

import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { uploadVideos } from "../lib/api";

export default function VideoUploader() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<FileList | null>(null);
  const [status, setStatus] = useState("");

  const upload = async () => {
    if (!files) return;
    setStatus("Processing...");
    const res = await uploadVideos(files);
    setStatus(`Uploaded: ${res.uploaded.join(", ")}`);
  };

  return (
    <div
      className="glass uploader"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        setFiles(e.dataTransfer.files);
      }}
    >
      <input
        hidden
        ref={inputRef}
        type="file"
        multiple
        accept="video/*"
        onChange={(e) => setFiles(e.target.files)}
      />

      <div className="uploader-left">
        <UploadCloud />
        <span>
          {files
            ? `${files.length} file(s) selected`
            : "Drag videos here or click upload"}
        </span>
      </div>

      <div className="uploader-actions">
        <button
          className="secondary-btn"
          onClick={() => inputRef.current?.click()}
        >
          Select
        </button>

        <button className="primary-btn" onClick={upload}>
          Upload
        </button>
      </div>

      {status && <div className="status">{status}</div>}
    </div>
  );
}