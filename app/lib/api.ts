const BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://chatbot-backend-zg1j.onrender.com";
export async function sendMessage(message: string, session_id: string) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id }),
  });
  return res.json();
}

export async function uploadVideos(files: FileList) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const res = await fetch(`${BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}

export async function getSessions() {
  const res = await fetch(`${BASE}/api/sessions`);
  return res.json();
}

export async function createSession() {
  const res = await fetch(`${BASE}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  return res.json();
}

export async function getMessages(session_id: string) {
  const res = await fetch(`${BASE}/api/sessions/${session_id}/messages`);
  return res.json();
}