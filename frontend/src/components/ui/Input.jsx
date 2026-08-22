import { useId } from "react";
import styles from "./Input.module.css";

export default function Input({
  label,
  error,
  helperText,
  icon: Icon,
  className = "",
  containerClassName = "",
  ...rest
}) {
  const id = useId();
  return (
    <div className={[styles.container, containerClassName].filter(Boolean).join(" ")}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <div className={styles.field}>
        {Icon && <Icon size={18} strokeWidth={2} className={styles.icon} aria-hidden="true" />}
        <input
          id={id}
          className={[styles.input, Icon ? styles.withIcon : "", error ? styles.hasError : "", className]
            .filter(Boolean)
            .join(" ")}
          aria-invalid={error ? "true" : undefined}
          aria-label={!label && rest.placeholder ? rest.placeholder : undefined}
          {...rest}
        />
      </div>
      {error ? (
        <p className={styles.errorText}>{error}</p>
      ) : helperText ? (
        <p className={styles.helperText}>{helperText}</p>
      ) : null}
    </div>
  );
}
