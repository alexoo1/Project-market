import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bell, MessageCircle, Package, Star, UserPlus, HandCoins,
} from "lucide-react";
import { getNotifications, markAllRead } from "../api/endpoints";
import SectionHeader from "../components/ui/SectionHeader";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { formatRelativeTime } from "../utils/formatTime";
import styles from "./NotificationsPage.module.css";

const TYPE_ICON = {
  new_message: MessageCircle,
  new_offer: HandCoins,
  offer_accepted: HandCoins,
  offer_rejected: HandCoins,
  offer_countered: HandCoins,
  order_paid: Package,
  order_shipped: Package,
  order_completed: Package,
  new_review: Star,
  new_follower: UserPlus,
};

function routeFor(n) {
  switch (n.type) {
    case "new_message":
      return n.related_entity_id ? `/messages/${n.related_entity_id}` : "/messages";
    case "order_paid":
    case "order_shipped":
    case "order_completed":
      return n.related_entity_id ? `/orders/${n.related_entity_id}` : "/profile";
    case "new_offer":
    case "offer_accepted":
    case "offer_rejected":
    case "offer_countered":
      return "/profile";
    case "new_follower":
      return n.related_entity_id ? `/users/${n.related_entity_id}` : "/profile";
    default:
      return "/profile";
  }
}

export default function NotificationsPage() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState(null);

  useEffect(() => {
    getNotifications().then(setNotifications).catch(() => setNotifications([]));
  }, []);

  const handleMarkAllRead = async () => {
    await markAllRead();
    setNotifications((list) => list.map((n) => ({ ...n, is_read: true })));
  };

  const hasUnread = notifications?.some((n) => !n.is_read);

  return (
    <div className={styles.page}>
      <SectionHeader
        title="Notifications"
        action={hasUnread && (
          <Button variant="ghost" size="md" onClick={handleMarkAllRead}>Tout marquer comme lu</Button>
        )}
      />

      {notifications === null && (
        <div className={styles.list}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className={styles.row}>
              <Skeleton variant="circle" width={38} height={38} />
              <Skeleton variant="text" width="70%" />
            </div>
          ))}
        </div>
      )}

      {notifications?.length === 0 && (
        <EmptyState icon={Bell} title="Aucune notification" description="Tu seras prévenu ici des messages, offres et mises à jour de commande." />
      )}

      {notifications?.length > 0 && (
        <div className={styles.list}>
          {notifications.map((n) => {
            const Icon = TYPE_ICON[n.type] || Bell;
            return (
              <button
                key={n.id}
                type="button"
                className={[styles.row, !n.is_read ? styles.unread : ""].filter(Boolean).join(" ")}
                onClick={() => navigate(routeFor(n))}
              >
                <div className={styles.icon}>
                  <Icon size={18} strokeWidth={1.75} />
                </div>
                <div className={styles.text}>
                  <p className={styles.title}>{n.title}</p>
                  {n.body && <p className={styles.body}>{n.body}</p>}
                  <p className={styles.time}>{formatRelativeTime(n.created_at)}</p>
                </div>
                {!n.is_read && <span className={styles.dot} aria-hidden="true" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
