import styles from "./UserAvatar.module.css";

export default function UserAvatar({ name, src, size = "md", className = "" }) {
  const initials = (name || "?").trim().slice(0, 2).toUpperCase();
  return (
    <div className={[styles.avatar, styles[size], className].filter(Boolean).join(" ")}>
      {src ? (
        <img src={src} alt="" className={styles.image} />
      ) : (
        <span aria-hidden="true">{initials}</span>
      )}
    </div>
  );
}
