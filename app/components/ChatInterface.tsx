"use client";

import { useEffect, useState, useRef } from "react";
import { sendMessage, getMessages } from "../lib/api";
import ChatInput from "./ChatInput";
import VideoUploader from "./VideoUploader";

export default function ChatInterface({ current }: any) {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [video, setVideo] = useState<any>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  const load = async () => {
    const data = await getMessages(current);
    setMessages(data);
  };

  useEffect(() => {
    load();
  }, [current]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const ask = async (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);

    const res = await sendMessage(text, current);

    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        content: res.answer,
        sources: res.sources || [],
      },
    ]);

    setLoading(false);
  };

  const speakText = (text: string) => {
    if (!text) return;

    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    const utter = new SpeechSynthesisUtterance(text);

    if (/[\u0980-\u09FF]/.test(text)) {
      utter.lang = "bn-IN";
    } else if (/[\u0900-\u097F]/.test(text)) {
      utter.lang = "hi-IN";
    } else {
      utter.lang = "en-IN";
    }

    utter.onstart = () => setSpeaking(true);
    utter.onend = () => setSpeaking(false);
    utter.onerror = () => setSpeaking(false);

    speechSynthesis.speak(utter);
  };

  const lastAnswer =
    [...messages]
      .reverse()
      .find((m) => m.role === "assistant")
      ?.content || "";

  return (
    <section className="main-panel">
      <div className="top-section">
        <VideoUploader />
      </div>

      <div className="chat-area">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`msg ${
              m.role === "user" ? "user-msg" : "bot-msg"
            } ${
              speaking &&
              m.role === "assistant" &&
              m.content === lastAnswer
                ? "speaking-highlight"
                : ""
            }`}
          >
            <div>{m.content}</div>

            {/* Restore timestamps */}
            {m.sources?.length > 0 && (
              <div className="source-list">
                {m.sources.map((s: any, idx: number) => (
                  <button
                    key={idx}
                    className="clip-btn"
                    onClick={() =>
                      setVideo({
                        url: s.video_url,
                        start: s.start,
                        title: s.video,
                      })
                    }
                  >
                    🎬 {s.video} ({Math.floor(s.start)}s)
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="msg bot-msg">Thinking...</div>
        )}

        <div ref={bottomRef}></div>
      </div>

      {/* Floating video player */}
      {video && (
        <div className="floating-player">
          <div className="player-header">
            <span>{video.title}</span>

            <button
              className="close-btn"
              onClick={() => setVideo(null)}
            >
              ✕
            </button>
          </div>

          <video
            controls
            autoPlay
            className="floating-video"
            src={`${video.url}#t=${Math.floor(video.start)}`}
          />
        </div>
      )}

      <ChatInput
        onSend={ask}
        lastAnswer={lastAnswer}
        onSpeakToggle={speakText}
        speaking={speaking}
      />
    </section>
  );
}