import styles from "./Skeleton.module.css";

export default function Skeleton({ variant = "rect", width, height, className = "", style = {} }) {
  return (
    <span
      className={[styles.skeleton, styles[variant], className].filter(Boolean).join(" ")}
      style={{ width, height, ...style }}
      aria-hidden="true"
    />
  );
}
