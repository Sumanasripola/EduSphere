import { useState, useEffect } from "react";
import PDFUploader from "../components/PDFUploader";
import ChatInterface from "../components/ChatInterface";
import { useAuth } from "../context/AuthContext";
import {
  listChatSessions,
  createChatSession,
  getSessionMessages,
  renameChatSession,
} from "../services/api";

export default function Dashboard() {
  const { isAuthenticated } = useAuth();

  // Each entry: { id: documentId, filename }
  const [allDocuments, setAllDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setChats([]);
      setActiveChatId(null);
      setLoadingSessions(false);
      return;
    }

    let cancelled = false;
    setLoadingSessions(true);

    listChatSessions()
      .then((sessions) => {
        if (cancelled) return;
        setChats(
          sessions.map((s) => ({
            id: s.id,
            name: s.name,
            documents: [], // recovered lazily from citations once opened — see handleSelectChat
            messages: [],
            messagesLoaded: false,
          }))
        );
      })
      .catch((err) => console.error("Failed to load chat sessions:", err))
      .finally(() => {
        if (!cancelled) setLoadingSessions(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  const handleFileUpload = (uploadedDocs) => {
    // uploadedDocs: [{ id, filename }, ...] from PDFUploader
    setAllDocuments((prev) => [...prev, ...uploadedDocs]);
  };

  const toggleDocument = (doc) => {
    setSelectedDocuments((prev) =>
      prev.some((d) => d.id === doc.id)
        ? prev.filter((d) => d.id !== doc.id)
        : [...prev, doc]
    );
  };

  const initializeChat = async () => {
    if (selectedDocuments.length === 0) {
      alert("Select at least one document first");
      return;
    }

    try {
      const saved = await createChatSession("New Chat");

      const newChat = {
        id: saved.id,
        documents: selectedDocuments,
        messages: [],
        name: null,
        messagesLoaded: true,
      };

      setChats((prev) => [...prev, newChat]);
      setActiveChatId(newChat.id);
      setSelectedDocuments([]);
    } catch (err) {
      console.error("Failed to create chat session:", err);
      alert("Couldn't start a new chat. Check that you're logged in and the backend is running.");
    }
  };

  const deleteChat = (chatId) => {
    setChats((prev) => prev.filter((chat) => chat.id !== chatId));
    if (chatId === activeChatId) setActiveChatId(null);
  };

  const updateMessages = (chatId, messages) => {
    setChats((prev) =>
      prev.map((chat) => {
        if (chat.id !== chatId) return chat;

        let chatName = chat.name;
        if (!chatName && messages.length > 0) {
          chatName = messages[0].text.slice(0, 30);
          renameChatSession(chatId, chatName).catch((err) =>
            console.error("Failed to save chat name:", err)
          );
        }

        return { ...chat, messages, name: chatName };
      })
    );
  };

  const handleSelectChat = async (chatId) => {
    setActiveChatId(chatId);

    const chat = chats.find((c) => c.id === chatId);
    if (!chat || chat.messagesLoaded) return;

    try {
      const rawMessages = await getSessionMessages(chatId);
      const mapped = rawMessages.map((m) => ({
        text: m.text,
        isUser: m.role === "user",
        images: m.images || [],
        excel: m.excel_path || null,
        citations: m.citations || [],
      }));

      // A reopened session doesn't know its original document_ids (sessions
      // don't store that yet — see the project status doc). Best-effort
      // recovery: pull the source filenames out of past citations so the
      // UI at least shows what this chat was about. Note these entries
      // have id: null, so a new question in this chat searches across all
      // of the user's documents rather than re-scoping to just these.
      const filenamesFromCitations = Array.from(
        new Set(mapped.flatMap((m) => (m.citations || []).map((c) => c.source)))
      ).filter(Boolean);

      const recoveredDocs = filenamesFromCitations.map((filename) => ({ id: null, filename }));

      setChats((prev) =>
        prev.map((c) =>
          c.id === chatId
            ? { ...c, messages: mapped, messagesLoaded: true, documents: recoveredDocs }
            : c
        )
      );
    } catch (err) {
      console.error("Failed to load messages for chat:", chatId, err);
    }
  };

  const activeChat = chats.find((chat) => chat.id === activeChatId);

  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="w-64 bg-black/40 backdrop-blur-lg p-4 text-white overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">Analysis Chats</h2>

        {loadingSessions && <p className="text-sm text-gray-400">Loading your chats...</p>}
        {!loadingSessions && chats.length === 0 && (
          <p className="text-sm text-gray-400">No chats yet — select documents and start one.</p>
        )}

        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`p-3 rounded mb-2 flex justify-between items-start ${
              chat.id === activeChatId ? "bg-blue-600" : "bg-white/10"
            }`}
          >
            <div className="flex-1 cursor-pointer" onClick={() => handleSelectChat(chat.id)}>
              <p className="text-sm font-medium">
                {chat.name ? chat.name : `Chat ${chat.id.toString().slice(-4)}`}
              </p>
              <p className="text-xs text-gray-300">
                {chat.documents.length > 0
                  ? chat.documents.map((d) => d.filename).join(", ")
                  : "—"}
              </p>
            </div>
            <button onClick={() => deleteChat(chat.id)} className="text-red-300 text-xs">
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="flex-1 grid grid-cols-3 gap-6 p-8 overflow-hidden">
        <div className="bg-white rounded-xl p-6 col-span-1 flex flex-col overflow-hidden">
          <h2 className="font-semibold mb-4">Document Library</h2>

          <PDFUploader onFileUpload={handleFileUpload} />

          <div className="flex-1 overflow-y-auto mt-4 pr-2">
            <div className="space-y-3">
              {allDocuments.map((doc) => {
                const isSelected = selectedDocuments.some((d) => d.id === doc.id);

                return (
                  <div
                    key={doc.id}
                    className={`flex items-center justify-between p-3 rounded-lg border transition cursor-pointer ${
                      isSelected ? "bg-blue-50 border-blue-400" : "bg-white border-gray-200 hover:bg-gray-50"
                    }`}
                    onClick={() => toggleDocument(doc)}
                  >
                    <p className="text-sm font-medium text-gray-700 truncate">{doc.filename}</p>

                    <div className="checkbox-wrapper">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleDocument(doc)}
                        id={`doc-${doc.id}`}
                      />
                      <label htmlFor={`doc-${doc.id}`}>
                        <div className="tick_mark"></div>
                      </label>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4">
            <button
              onClick={initializeChat}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl shadow-lg hover:scale-105 transition"
            >
              Initialize Chat
            </button>
          </div>
        </div>

        <div className="bg-gradient-to-b from-white to-gray-50 rounded-2xl p-6 col-span-2 flex flex-col overflow-hidden shadow-lg border border-gray-200">
          {activeChat ? (
            <ChatInterface chat={activeChat} updateMessages={updateMessages} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              Select documents and initialize a chat
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
