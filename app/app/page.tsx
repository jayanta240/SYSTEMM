"use client";

import { useState } from "react";
import ChatSidebar from "../components/ChatSidebar";
import ChatInterface from "../components/ChatInterface";

export default function Home() {
  const [current, setCurrent] = useState("chat-1");

  return (
    <main className="layout">
      <ChatSidebar
        current={current}
        setCurrent={setCurrent}
      />

      <ChatInterface current={current} />
    </main>
  );
}