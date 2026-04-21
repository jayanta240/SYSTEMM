"use client";

import { useState } from "react";
import { Mic, Send, Volume2 } from "lucide-react";

export default function ChatInput({
  onSend,
  lastAnswer,
  onSpeakToggle,
  speaking,
}: any) {
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);

  const startVoice = () => {
    const SpeechRecognition =
      (window as any).webkitSpeechRecognition ||
      (window as any).SpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition not supported.");
      return;
    }

    const recog = new SpeechRecognition();
    recog.lang = navigator.language || "en-IN";
    recog.interimResults = false;
    recog.continuous = false;

    setListening(true);

    recog.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      setText(transcript);
      onSend(transcript);
      setText("");
    };

    recog.onend = () => setListening(false);

    recog.start();
  };

  return (
    <div className="input-bar">
      <input
        className="input-box"
        placeholder="Ask about videos..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && text.trim()) {
            onSend(text);
            setText("");
          }
        }}
      />

      <button
        className={`icon-btn ${listening ? "wave" : ""}`}
        onClick={startVoice}
        title="Voice Input"
      >
        <Mic size={18} />
      </button>

      <button
        className={`icon-btn ${speaking ? "active-tts" : ""}`}
        onClick={() => onSpeakToggle(lastAnswer)}
        title={speaking ? "Stop Reading" : "Read Answer"}
      >
        <Volume2 size={18} />
      </button>

      <button
        className="primary-btn"
        onClick={() => {
          if (!text.trim()) return;
          onSend(text);
          setText("");
        }}
      >
        <Send size={18} />
      </button>
    </div>
  );
}