"use client";

import { useState } from "react";

export default function IssuesPage() {

  const [file, setFile] = useState<File | null>(null);
  const [problem, setProblem] = useState("");
  const [solution, setSolution] = useState("");

  const handleSubmit = async () => {

    if (!file || !problem || !solution) {
      alert("Fill all fields");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);
    formData.append("problem", problem);
    formData.append("solution", solution);

    const res = await fetch(
      "http://127.0.0.1:8000/api/upload-issue",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    if (data.success) {
      alert("Issue Saved");

      setProblem("");
      setSolution("");
      setFile(null);
    }
  };

  return (
    <div className="p-8">

      <h1 className="text-3xl font-bold mb-6">
        Issue Knowledge Base
      </h1>

      <div className="space-y-4 max-w-xl">

        <input
          type="file"
          accept="image/*"
          onChange={(e) =>
            setFile(e.target.files?.[0] || null)
          }
        />

        <input
          value={problem}
          onChange={(e) =>
            setProblem(e.target.value)
          }
          placeholder="Problem Name"
          className="w-full p-3 rounded bg-gray-800"
        />

        <textarea
          value={solution}
          onChange={(e) =>
            setSolution(e.target.value)
          }
          placeholder="Solution"
          className="w-full p-3 rounded bg-gray-800 h-40"
        />

        <button
          onClick={handleSubmit}
          className="bg-green-600 px-5 py-3 rounded"
        >
          Save Issue
        </button>

      </div>
    </div>
  );
}