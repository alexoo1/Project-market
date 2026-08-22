import Chip from "./Chip";
import styles from "./FilterChip.module.css";

export default function FilterChip({ icon: Icon, active, onClick, children }) {
  return (
    <Chip active={active} onClick={onClick} className={styles.chip}>
      {Icon && <Icon size={14} strokeWidth={2} aria-hidden="true" />}
      {children}
    </Chip>
  );
}
