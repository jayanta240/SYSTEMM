"use client";

import { useEffect, useState } from "react";
import { getSessions, createSession } from "../lib/api";

export default function ChatSidebar({
  current,
  setCurrent,
}: any) {
  const [sessions, setSessions] = useState<any[]>([]);

  const load = async () => {
    const data = await getSessions();
    setSessions(data);
  };

  useEffect(() => {
    load();
  }, []);

  const newChat = async () => {
    const s = await createSession();
    setCurrent(s.id);
    load();
  };

  return (
    <aside className="sidebar">
      <div>
        <h1 className="logo">CPUTEK AI</h1>

        <button className="primary-btn full" onClick={newChat}>
          + New Chat
        </button>

        <div className="session-list">
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => setCurrent(s.id)}
              className={`session-item ${
                current === s.id ? "active" : ""
              }`}
            >
              {s.name}
            </button>
          ))}
        </div>
      </div>

      <div className="small-text">
        AI Video Assistant
      </div>
    </aside>
  );
}