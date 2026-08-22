import styles from "./EmptyState.module.css";

export default function EmptyState({ icon: Icon, title, description, action, className = "" }) {
  return (
    <div className={[styles.container, className].filter(Boolean).join(" ")}>
      {Icon && (
        <div className={styles.iconWrap}>
          <Icon size={26} strokeWidth={1.75} aria-hidden="true" />
        </div>
      )}
      <p className={styles.title}>{title}</p>
      {description && <p className={styles.description}>{description}</p>}
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
