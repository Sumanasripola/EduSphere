import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Automatically attach the saved token (if any) to every outgoing request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- Auth ----------

export const registerUser = async (email, password) => {
  const res = await API.post("/auth/register", { email, password });
  return res.data; // { access_token, user }
};

export const loginUser = async (email, password) => {
  const res = await API.post("/auth/login", { email, password });
  return res.data; // { access_token, user }
};

// ---------- Chat sessions ----------

export const createChatSession = async (name) => {
  const res = await API.post("/chat/sessions", { name });
  return res.data;
};

export const listChatSessions = async () => {
  const res = await API.get("/chat/sessions");
  return res.data;
};

export const renameChatSession = async (sessionId, name) => {
  const res = await API.patch(`/chat/sessions/${sessionId}`, { name });
  return res.data;
};

export const getSessionMessages = async (sessionId) => {
  const res = await API.get(`/chat/sessions/${sessionId}/messages`);
  return res.data;
};

export const saveMessage = async (sessionId, role, text, citations = [], images = [], excelPath = null) => {
  const res = await API.post(`/chat/sessions/${sessionId}/messages`, {
    role,
    text,
    citations,
    images,
    excel_path: excelPath,
  });
  return res.data;
};

// ---------- Existing document endpoints (unchanged) ----------

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data; // { message, document_id, chunks_indexed }
};

export const askQuestion = async (question, documentIds) => {
  const res = await API.post("/query/", { question, document_ids: documentIds });
  return res.data;
};
