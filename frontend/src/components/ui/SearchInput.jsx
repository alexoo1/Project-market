import { Search, X } from "lucide-react";
import styles from "./SearchInput.module.css";

export default function SearchInput({ value, onChange, onClear, className = "", ...rest }) {
  return (
    <div className={[styles.field, className].filter(Boolean).join(" ")}>
      <Search size={18} strokeWidth={2} className={styles.icon} aria-hidden="true" />
      <input
        type="search"
        className={styles.input}
        value={value}
        onChange={onChange}
        aria-label={rest.placeholder}
        {...rest}
      />
      {value && (
        <button type="button" className={styles.clear} onClick={onClear} aria-label="Effacer la recherche">
          <X size={15} strokeWidth={2} />
        </button>
      )}
    </div>
  );
}
