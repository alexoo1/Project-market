import { Star } from "lucide-react";
import styles from "./RatingStars.module.css";

export default function RatingStars({ value = 0, count = 5, size = 15, interactive = false, onChange, className = "" }) {
  const stars = Array.from({ length: count }, (_, i) => i + 1);

  return (
    <div
      className={[styles.stars, interactive ? styles.interactive : "", className].filter(Boolean).join(" ")}
      role={interactive ? "radiogroup" : undefined}
      aria-label={interactive ? "Note" : `Note : ${value} sur ${count}`}
    >
      {stars.map((n) =>
        interactive ? (
          <button
            key={n}
            type="button"
            role="radio"
            aria-checked={n === value}
            aria-label={`${n} étoile${n > 1 ? "s" : ""}`}
            className={styles.starButton}
            onClick={() => onChange?.(n)}
          >
            <Star size={size + 6} strokeWidth={1.75} fill={n <= value ? "currentColor" : "none"} className={n <= value ? styles.filled : styles.empty} />
          </button>
        ) : (
          <Star
            key={n}
            size={size}
            strokeWidth={1.75}
            fill={n <= Math.round(value) ? "currentColor" : "none"}
            className={n <= Math.round(value) ? styles.filled : styles.empty}
            aria-hidden="true"
          />
        )
      )}
    </div>
  );
}
