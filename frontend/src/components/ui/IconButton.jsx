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
      <Icon size={size === "sm" ? 20 : 22} strokeWidth={1.75} aria-hidden="true" />
    </button>
  );
}
