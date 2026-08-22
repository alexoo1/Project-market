import styles from "./Chip.module.css";

export default function Chip({ active = false, onClick, children, className = "", ...rest }) {
  const classes = [styles.chip, active ? styles.active : "", className].filter(Boolean).join(" ");

  if (!onClick) {
    return (
      <span className={classes} {...rest}>
        {children}
      </span>
    );
  }

  return (
    <button type="button" onClick={onClick} className={classes} aria-pressed={active} {...rest}>
      {children}
    </button>
  );
}
