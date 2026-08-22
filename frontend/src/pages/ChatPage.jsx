import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Send, Check, CheckCheck } from "lucide-react";
import { getMessages, sendMessage, getConversation } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import IconButton from "../components/ui/IconButton";
import UserAvatar from "../components/ui/UserAvatar";
import Skeleton from "../components/ui/Skeleton";
import { formatMessageTime } from "../utils/formatTime";
import styles from "./ChatPage.module.css";

function UserHeader({ other, listing }) {
  const content = (
    <>
      <UserAvatar name={other.display_name} src={other.profile_photo_url} size="sm" />
      <div>
        <p className={styles.headerName}>{other.display_name}</p>
        {listing && <p className={styles.headerListing}>{listing.title}</p>}
      </div>
    </>
  );
  return listing ? (
    <Link to={`/listings/${listing.id}`} className={styles.headerUser}>
      {content}
    </Link>
  ) : (
    <div className={styles.headerUser}>{content}</div>
  );
}

export default function ChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);

  const load = () => getMessages(id).then(setMessages).finally(() => setLoading(false));

  useEffect(() => {
    getConversation(id).then(setConversation).catch(() => {});
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

  const other = conversation?.other_participant;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <IconButton icon={ArrowLeft} label="Retour" onClick={() => navigate(-1)} />
        {other ? (
          <UserHeader other={other} listing={conversation.listing} />
        ) : (
          <Skeleton variant="circle" width={32} height={32} />
        )}
      </div>

      <div className={styles.thread}>
        {loading && (
          <div className={styles.loadingState}>
            <Skeleton variant="text" width="50%" />
          </div>
        )}
        {messages.map((m) => {
          const isMine = m.sender_id === user?.id;
          return (
            <div key={m.id} className={[styles.messageRow, isMine ? styles.mine : styles.theirs].join(" ")}>
              <div className={styles.bubble}>{m.content}</div>
              <div className={styles.meta}>
                <span>{formatMessageTime(m.created_at)}</span>
                {isMine && (m.is_read ? <CheckCheck size={13} strokeWidth={2} /> : <Check size={13} strokeWidth={2} />)}
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className={styles.composer}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Écrire un message..."
          aria-label="Écrire un message"
          className={styles.input}
        />
        <IconButton icon={Send} label="Envoyer" variant="filled" type="submit" disabled={!text.trim()} />
      </form>
    </div>
  );
}
