import styles from "./IconButton.module.css";

export default function IconButton({
  icon: Icon,
  label,
  variant = "ghost",
  size = "md",
  className = "",
  ...rest
}) {
  return (
    <button
      type="button"
      aria-label={label}
      className={[styles.button, styles[variant], styles[size], className].filter(Boolean).join(" ")}
      {...rest}
    >
      <Icon size={size === "sm" ? 16 : 20} strokeWidth={2} aria-hidden="true" />
    </button>
  );
}
