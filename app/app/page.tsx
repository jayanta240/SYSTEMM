"use client";
import ReactMarkdown from "react-markdown";

import { useState, useEffect, useRef } from "react";
import {
  sendMessage,
  uploadVideos,
  generateVideo,
  getMessages,
  createSession,
} from "../lib/api";

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [session, setSession] = useState("chat-1");
  const [loading, setLoading] = useState(false);
  const [videoLoading, setVideoLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages(session);
  }, [session]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadMessages = async (sid: string) => {
    const data = await getMessages(sid);
    setMessages(data || []);
  };

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMsg = { role: "user", content: message };
    setMessages((prev) => [...prev, userMsg]);

    setLoading(true);

    const res = await sendMessage(message, session);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
      },
    ]);

    setLoading(false);
    setMessage("");
  };

  const handleUpload = async (e: any) => {
    const files = e.target.files;
    if (!files.length) return;

    setLoading(true);
    const res = await uploadVideos(files);
    alert("Uploaded: " + res.uploaded.join(", "));
    setLoading(false);
  };

  const handleGenerateVideo = async (msg: string) => {
    setVideoLoading(true);

    const res = await generateVideo(msg);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "🎥 Generated Explanation Video",
        video: res.video_path,
      },
    ]);

    setVideoLoading(false);
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* SIDEBAR */}
      <div className="w-64 bg-gray-800 p-4 flex flex-col">
        <h1 className="text-xl font-bold mb-4">CPUTEK</h1>

        <button
          onClick={async () => {
            const s = await createSession();
            setSession(s.id);
          }}
          className="bg-blue-600 hover:bg-blue-700 p-2 rounded mb-4"
        >
          + New Chat
        </button>

        <div className="text-sm text-gray-400">Session: {session}</div>
      </div>

      {/* MAIN */}
      <div className="flex flex-col flex-1">
        {/* TOP BAR */}
        <div className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="text-lg font-semibold">Learning Assistant</h2>

          <label className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded cursor-pointer text-sm">
           📁 Upload Files
           <input
              type="file"
              multiple
              onChange={handleUpload}
              className="hidden"
           />
          </label>
        </div>

        {/* CHAT */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-3xl ${
                m.role === "user" ? "ml-auto text-right" : ""
              }`}
            >
              <div
                className={`inline-block px-4 py-3 rounded-xl ${
                  m.role === "user"
                    ? "bg-blue-600"
                    : "bg-gray-800 border border-gray-700"
                }`}
              >
                <div style={{ color: "white", lineHeight: "1.6" }}>
                  <ReactMarkdown>
                      {m.content}
                  </ReactMarkdown>
                </div>

                {/* SOURCES */}
                {m.sources && (
                  <div className="mt-3 text-sm text-gray-400 space-y-2">
                    {m.sources.map((s: any, idx: number) => (
                      <div key={idx}>
                        {s.video_url ? (
                          <>
                            <p>
                              🎥 {s.video} ({s.start?.toFixed(1)}s -{" "}
                              {s.end?.toFixed(1)}s)
                            </p>
                            <video
                              src={`${s.video_url}#t=${Math.floor(s.start || 0)}`}
                              controls
                              className="mt-2 rounded w-full"
                            />
                          </>
                        ) : (
                          <p>
                            📄 {s.source} (Page {s.page})
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* GENERATED VIDEO */}
                {m.video && (
                  <>
                   <video
                     src={`http://localhost:8000/${m.video}`}
                     controls
                     className="mt-3 rounded w-full"
                   />
                   <p className="text-green-400 text-sm mt-2">
                      ✅ Video ready
                   </p>
                  </>
                )}

                {/* BUTTON */}
                {m.role === "assistant" && !m.video &&(
                  <button
                    onClick={() => handleGenerateVideo(m.content)}
                    disabled={videoLoading}
                    className={`mt-3 px-3 py-1 rounded text-sm ${
                       videoLoading
                          ? "bg-gray-600 cursor-not-allowed"
                          : "bg-purple-600 hover:bg-purple-700"
                   }`}
                  >
                   {videoLoading ? "⏳ Generating..." : "🎥 Generate Video"}
                  </button>
                )}
              </div>
            </div>
          ))}

          {loading && <p className="text-gray-400">Thinking...</p>}
          {videoLoading && (
            <p className="text-purple-400">Generating video...</p>
          )}

          <div ref={bottomRef} />
        </div>

        {/* INPUT */}
        <div className="p-4 border-t border-gray-700 flex gap-3">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask anything about your content..."
            className="flex-1 bg-gray-800 p-3 rounded-lg outline-none"
          />

          <button
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-700 px-5 rounded-lg"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}