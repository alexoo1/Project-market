import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getMessages, sendMessage } from "../api/endpoints";
import { COLORS } from "../theme";
import { useAuth } from "../context/AuthContext";

export default function ChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);

  const load = () => getMessages(id).then(setMessages).finally(() => setLoading(false));

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    const content = text;
    setText("");
    await sendMessage(id, content);
    load();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 16px", borderBottom: `1px solid ${COLORS.sandDeep}` }}>
        <button onClick={() => navigate(-1)} style={{ border: "none", background: "none", fontSize: 18, cursor: "pointer" }}>←</button>
        <p style={{ margin: 0, fontWeight: 600, fontSize: 14 }}>Conversation</p>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
        {loading && <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Chargement...</p>}
        {messages.map((m) => {
          const isMine = m.sender_id === user?.id;
          return (
            <div key={m.id} style={{ display: "flex", justifyContent: isMine ? "flex-end" : "flex-start" }}>
              <div
                style={{
                  maxWidth: "75%", padding: "8px 14px", borderRadius: 16, fontSize: 13.5,
                  background: isMine ? COLORS.lagoon : "#fff", color: isMine ? COLORS.sand : COLORS.ink,
                }}
              >
                {m.content}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} style={{ display: "flex", gap: 8, padding: 12, borderTop: `1px solid ${COLORS.sandDeep}` }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Écrire un message..."
          style={{ flex: 1, padding: "10px 16px", borderRadius: 999, border: `1px solid ${COLORS.sandDeep}`, fontSize: 13.5 }}
        />
        <button type="submit" style={{ width: 40, height: 40, borderRadius: "50%", border: "none", background: COLORS.coral, color: "#fff", cursor: "pointer" }}>
          ➤
        </button>
      </form>
    </div>
  );
}
