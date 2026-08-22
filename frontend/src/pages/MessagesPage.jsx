import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getConversations } from "../api/endpoints";
import { COLORS } from "../theme";
import { useAuth } from "../context/AuthContext";

export default function MessagesPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/login");
      return;
    }
    if (user) {
      getConversations().then(setConversations).finally(() => setLoading(false));
    }
  }, [user, authLoading, navigate]);

  return (
    <div style={{ padding: "16px 0 80px" }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, color: COLORS.lagoon, padding: "0 16px" }}>Messages</h1>
      {loading && <p style={{ padding: "0 16px", color: COLORS.inkSoft, fontSize: 13 }}>Chargement...</p>}
      {!loading && conversations.length === 0 && (
        <p style={{ padding: "0 16px", color: COLORS.inkSoft, fontSize: 13 }}>Aucune conversation pour le moment.</p>
      )}
      <div>
        {conversations.map((c) => (
          <Link
            key={c.id}
            to={`/messages/${c.id}`}
            style={{
              display: "flex", gap: 10, padding: "12px 16px", textDecoration: "none", color: "inherit",
              borderBottom: `1px solid ${COLORS.sandDeep}`, alignItems: "center",
            }}
          >
            <div style={{ width: 44, height: 44, borderRadius: "50%", background: COLORS.lagoon, color: COLORS.sand, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 600, flexShrink: 0 }}>
              💬
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ margin: 0, fontSize: 13.5, fontWeight: c.unread_count > 0 ? 700 : 500 }}>
                {c.last_message?.content || "Nouvelle conversation"}
              </p>
              <p style={{ margin: 0, fontSize: 11.5, color: COLORS.inkSoft }}>
                {c.unread_count > 0 ? `${c.unread_count} non lu(s)` : "Lu"}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
