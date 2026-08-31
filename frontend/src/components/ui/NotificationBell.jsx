import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell } from "lucide-react";
import { getUnreadCount } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";
import styles from "./NotificationBell.module.css";

export default function NotificationBell({ className = "" }) {
  const { user } = useAuth();
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!user) return;
    getUnreadCount().then((d) => setCount(d.count)).catch(() => {});
  }, [user]);

  if (!user) return null;

  return (
    <Link to="/notifications" aria-label="Notifications" className={[styles.bell, className].filter(Boolean).join(" ")}>
      <Bell size={22} strokeWidth={1.75} />
      {count > 0 && <span className={styles.badge}>{count > 9 ? "9+" : count}</span>}
    </Link>
  );
}
