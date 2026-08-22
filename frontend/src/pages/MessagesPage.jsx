import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { MessageCircle } from "lucide-react";
import { getConversations } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import UserAvatar from "../components/ui/UserAvatar";
import Skeleton from "../components/ui/Skeleton";
import EmptyState from "../components/ui/EmptyState";
import SectionHeader from "../components/ui/SectionHeader";
import { formatRelativeTime } from "../utils/formatTime";
import styles from "./MessagesPage.module.css";

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
    <div className={styles.page}>
      <SectionHeader title="Messages" className={styles.header} />

      {loading && (
        <div className={styles.list}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className={styles.row}>
              <Skeleton variant="circle" width={44} height={44} />
              <div className={styles.rowText}>
                <Skeleton variant="text" width="60%" />
                <Skeleton variant="text" width="40%" style={{ marginTop: 6 }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && conversations.length === 0 && (
        <EmptyState
          icon={MessageCircle}
          title="Aucune conversation"
          description="Contacte un vendeur depuis une annonce pour démarrer une discussion."
        />
      )}

      <div className={styles.list}>
        {conversations.map((c) => (
          <Link key={c.id} to={`/messages/${c.id}`} className={styles.row}>
            <UserAvatar name={c.other_participant?.display_name} src={c.other_participant?.profile_photo_url} />
            <div className={styles.rowText}>
              <div className={styles.rowTop}>
                <p className={[styles.name, c.unread_count > 0 ? styles.unread : ""].join(" ")}>
                  {c.other_participant?.display_name}
                </p>
                {c.last_message_at && (
                  <span className={styles.time}>{formatRelativeTime(c.last_message_at)}</span>
                )}
              </div>
              <div className={styles.rowBottom}>
                <p className={[styles.preview, c.unread_count > 0 ? styles.unread : ""].join(" ")}>
                  {c.last_message?.content || "Nouvelle conversation"}
                </p>
                {c.unread_count > 0 && <span className={styles.badge}>{c.unread_count}</span>}
              </div>
              {c.listing && <p className={styles.listingRef}>{c.listing.title}</p>}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
