import { NavLink, Link } from "react-router-dom";
import { Search, MessageCircle, Plus } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import UserAvatar from "./UserAvatar";
import Button from "./Button";
import NotificationBell from "./NotificationBell";
import styles from "./Navbar.module.css";

const links = [
  { to: "/", label: "Accueil", end: true },
  { to: "/search", label: "Rechercher" },
];

export default function Navbar() {
  const { user } = useAuth();

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link to="/" className={styles.logo}>
          <img src="/logo-mark.png" alt="" className={styles.logoMark} />
          <img src="/wordmark.png" alt="Vendoo" className={styles.wordmark} />
        </Link>

        <nav className={styles.links} aria-label="Navigation principale">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => [styles.link, isActive ? styles.active : ""].filter(Boolean).join(" ")}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className={styles.actions}>
          <Link to="/search" className={styles.iconLink} aria-label="Rechercher">
            <Search size={22} strokeWidth={1.75} />
          </Link>
          <Link to="/messages" className={styles.iconLink} aria-label="Messages">
            <MessageCircle size={22} strokeWidth={1.75} />
          </Link>
          <NotificationBell className={styles.iconLink} />
          <Link to="/sell">
            <Button variant="primary" size="md" className={styles.sellButton}>
              <Plus size={20} strokeWidth={1.75} />
              Vendre
            </Button>
          </Link>
          <Link to={user ? "/profile" : "/login"} aria-label="Profil" className={styles.avatarLink}>
            <UserAvatar name={user?.display_name} src={user?.profile_photo_url} size="sm" />
          </Link>
        </div>
      </div>
    </header>
  );
}
