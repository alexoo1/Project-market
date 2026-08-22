import { AnimatePresence, m } from "motion/react";
import { X } from "lucide-react";
import { useEffect } from "react";
import IconButton from "./IconButton";
import styles from "./Modal.module.css";

export default function Modal({ open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose?.();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <div className={styles.overlay}>
          <m.div
            className={styles.backdrop}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={onClose}
          />
          <m.div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            className={styles.panel}
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8, transition: { duration: 0.15 } }}
            transition={{ duration: 0.2, ease: [0.2, 0, 0, 1] }}
          >
            <div className={styles.header}>
              {title && <p className={styles.title}>{title}</p>}
              <IconButton icon={X} label="Fermer" size="sm" onClick={onClose} className={styles.close} />
            </div>
            <div className={styles.body}>{children}</div>
          </m.div>
        </div>
      )}
    </AnimatePresence>
  );
}
