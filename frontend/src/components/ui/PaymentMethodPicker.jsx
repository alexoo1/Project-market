import { CreditCard, Smartphone, Waves } from "lucide-react";
import { PAYMENT_METHOD_LABELS } from "../../theme";
import styles from "./PaymentMethodPicker.module.css";

const METHODS = [
  { value: "card", icon: CreditCard },
  { value: "orange_money", icon: Smartphone },
  { value: "mtn_mobile_money", icon: Smartphone },
  { value: "wave", icon: Waves },
];

export default function PaymentMethodPicker({ value, onChange, label = "Moyen de paiement" }) {
  return (
    <div className={styles.container}>
      {label && <p className={styles.label}>{label}</p>}
      <div className={styles.grid} role="radiogroup" aria-label={label}>
        {METHODS.map((m) => {
          const Icon = m.icon;
          const active = value === m.value;
          return (
            <button
              key={m.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => onChange(m.value)}
              className={[styles.option, active ? styles.active : ""].filter(Boolean).join(" ")}
            >
              <Icon size={18} strokeWidth={2} aria-hidden="true" />
              <span>{PAYMENT_METHOD_LABELS[m.value]}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
