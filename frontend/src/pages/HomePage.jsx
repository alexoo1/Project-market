import { useEffect, useState } from "react";
import { PackageSearch } from "lucide-react";
import { getCategories, searchListings } from "../api/endpoints";
import ListingCard, { ListingCardSkeleton } from "../components/ListingCard";
import Chip from "../components/ui/Chip";
import EmptyState from "../components/ui/EmptyState";
import { useAuth } from "../context/AuthContext";
import styles from "./HomePage.module.css";

export default function HomePage() {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    searchListings({ category_id: activeCategory || undefined, page_size: 20 })
      .then((data) => setListings(data.items))
      .catch(() => setError("Impossible de charger les annonces."))
      .finally(() => setLoading(false));
  }, [activeCategory]);

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        {user && <p className={styles.location}>{user.city || "Côte d'Ivoire"}</p>}
        <h1 className={styles.title}>Project Market</h1>
      </div>

      <div className={styles.chips}>
        <Chip active={!activeCategory} onClick={() => setActiveCategory(null)}>
          Tout
        </Chip>
        {categories.map((c) => (
          <Chip key={c.id} active={activeCategory === c.id} onClick={() => setActiveCategory(c.id)}>
            {c.name}
          </Chip>
        ))}
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {loading ? (
        <div className={styles.grid}>
          {Array.from({ length: 6 }).map((_, i) => (
            <ListingCardSkeleton key={i} />
          ))}
        </div>
      ) : listings.length === 0 ? (
        <EmptyState
          icon={PackageSearch}
          title="Aucune annonce pour le moment"
          description="Reviens un peu plus tard ou explore une autre catégorie."
        />
      ) : (
        <div className={styles.grid}>
          {listings.map((l) => (
            <ListingCard key={l.id} listing={l} />
          ))}
        </div>
      )}
    </div>
  );
}
