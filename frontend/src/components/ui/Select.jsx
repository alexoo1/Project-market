import { useId } from "react";
import { ChevronDown } from "lucide-react";
import styles from "./Select.module.css";

export default function Select({ label, className = "", containerClassName = "", children, ...rest }) {
  const id = useId();
  return (
    <div className={[styles.container, containerClassName].filter(Boolean).join(" ")}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <div className={styles.field}>
        <select id={id} className={[styles.select, className].filter(Boolean).join(" ")} {...rest}>
          {children}
        </select>
        <ChevronDown size={18} strokeWidth={2} className={styles.chevron} aria-hidden="true" />
      </div>
    </div>
  );
}
