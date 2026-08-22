import styles from "./SectionHeader.module.css";

export default function SectionHeader({ title, subtitle, action, className = "" }) {
  return (
    <div className={[styles.header, className].filter(Boolean).join(" ")}>
      <div>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}
