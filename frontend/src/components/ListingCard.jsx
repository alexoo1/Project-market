import { useState } from "react";
import { Link } from "react-router-dom";
import { Heart, ImageOff } from "lucide-react";
import { formatFCFA, CONDITION_LABELS } from "../theme";
import { addFavorite, removeFavorite } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { useToast } from "./ui/ToastProvider";
import Skeleton from "./ui/Skeleton";
import styles from "./ListingCard.module.css";

export function ListingCardSkeleton() {
  return (
    <div className={styles.card}>
      <div className={styles.imageWrap}>
        <Skeleton className={styles.image} />
      </div>
      <div className={styles.info}>
        <Skeleton variant="text" width="50%" />
        <Skeleton variant="text" width="80%" style={{ marginTop: 6 }} />
        <Skeleton variant="text" width="40%" style={{ marginTop: 6 }} />
      </div>
    </div>
  );
}

export default function ListingCard({ listing, isFavorited = false }) {
  const { user } = useAuth();
  const toast = useToast();
  const [favorited, setFavorited] = useState(isFavorited);
  const [busy, setBusy] = useState(false);

  const toggleFavorite = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) {
      toast.info("Connecte-toi pour ajouter des favoris.");
      return;
    }
    if (busy) return;
    const next = !favorited;
    setFavorited(next);
    setBusy(true);
    try {
      if (next) {
        await addFavorite(listing.id);
        toast.success("Ajouté aux favoris");
      } else {
        await removeFavorite(listing.id);
        toast.info("Retiré des favoris");
      }
    } catch {
      setFavorited(!next);
      toast.error("Une erreur est survenue.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Link to={`/listings/${listing.id}`} className={styles.card}>
      <div className={styles.imageWrap}>
        {listing.cover_image_url ? (
          <img src={listing.cover_image_url} alt={listing.title} className={styles.image} loading="lazy" />
        ) : (
          <div className={styles.placeholder}>
            <ImageOff size={22} strokeWidth={1.75} aria-hidden="true" />
          </div>
        )}
        <button
          type="button"
          onClick={toggleFavorite}
          className={[styles.favoriteButton, favorited ? styles.favorited : ""].filter(Boolean).join(" ")}
          aria-label={favorited ? "Retirer des favoris" : "Ajouter aux favoris"}
          aria-pressed={favorited}
        >
          <Heart size={18} strokeWidth={1.75} fill={favorited ? "currentColor" : "none"} />
        </button>
        {listing.condition && (
          <span className={styles.conditionTag}>{CONDITION_LABELS[listing.condition]}</span>
        )}
      </div>
      <div className={styles.info}>
        <p className={styles.price}>{formatFCFA(listing.price)}</p>
        <p className={styles.title}>{listing.title}</p>
        <p className={styles.city}>{listing.city}</p>
      </div>
    </Link>
  );
}
