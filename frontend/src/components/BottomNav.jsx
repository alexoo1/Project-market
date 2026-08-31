import { NavLink } from "react-router-dom";
import { Home, Search, Plus, MessageCircle, User } from "lucide-react";
import styles from "./BottomNav.module.css";

const items = [
  { to: "/", label: "Accueil", icon: Home },
  { to: "/search", label: "Recherche", icon: Search },
  { to: "/sell", label: "Vendre", icon: Plus, isCenter: true },
  { to: "/messages", label: "Messages", icon: MessageCircle },
  { to: "/profile", label: "Profil", icon: User },
];

export default function BottomNav() {
  return (
    <nav className={styles.nav} aria-label="Navigation principale">
      {items.map((item) =>
        item.isCenter ? (
          <div key={item.to} className={styles.centerSlot}>
            <NavLink to={item.to} className={styles.fab} aria-label={item.label}>
              <item.icon size={22} strokeWidth={1.75} aria-hidden="true" />
            </NavLink>
          </div>
        ) : (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => [styles.item, isActive ? styles.active : ""].filter(Boolean).join(" ")}
          >
            <item.icon size={22} strokeWidth={1.75} aria-hidden="true" />
            <span>{item.label}</span>
          </NavLink>
        )
      )}
    </nav>
  );
}
