const BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export async function generateVideo(message: string) {
  const res = await fetch(`${BASE}/api/generate-video`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: "chat-1" }),
  });

  return res.json();
}

export async function getMessages(session_id: string) {
  const res = await fetch(`${BASE}/api/sessions/${session_id}/messages`);
  return res.json();
}

export async function createSession() {
  const res = await fetch(`${BASE}/api/sessions`, {
    method: "POST",
  });
  return res.json();
}

export async function uploadImage(file: File) {

  const form = new FormData();

  form.append("file", file);

  const res = await fetch(
    `${BASE}/api/upload-image`,
    {
      method: "POST",
      body: form,
    }
  );

  return res.json();
}
export async function diagnoseImage(
  file: File
) {

  const form = new FormData();

  form.append("file", file);

  const res = await fetch(
    `${BASE}/api/diagnose-image`,
    {
      method: "POST",
      body: form,
    }
  );

  return res.json();
}