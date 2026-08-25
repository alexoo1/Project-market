import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search as SearchIcon, Venus, Mars, Baby, Footprints, ShoppingBag, Gem, Shirt, Zap, Tag,
} from "lucide-react";
import { getCategories } from "../api/endpoints";
import NotificationBell from "../components/ui/NotificationBell";
import Skeleton from "../components/ui/Skeleton";
import { useAuth } from "../context/AuthContext";
import styles from "./HomePage.module.css";

const CATEGORY_ICONS = {
  femme: Venus,
  homme: Mars,
  enfant: Baby,
  chaussures: Footprints,
  sacs: ShoppingBag,
  accessoires: Gem,
  streetwear: Shirt,
  sneakers: Zap,
};

const ICON_TONES = ["tone1", "tone2", "tone3", "tone4"];

export default function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  const goSearch = () => {
    if (!q.trim()) return navigate("/search");
    navigate("/search", { state: { q: q.trim() } });
  };

  const openCategory = (c) => {
    navigate("/search", { state: { categoryId: c.id, categoryName: c.name } });
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <img src="/favicon.svg" alt="" className={styles.logoMark} />
          <div>
            {user && <p className={styles.location}>{user.city || "Côte d'Ivoire"}</p>}
            <h1 className={styles.title}>Vendi Market</h1>
          </div>
        </div>
        <NotificationBell className={styles.bell} />
      </div>

      <form
        className={styles.searchRow}
        onSubmit={(e) => {
          e.preventDefault();
          goSearch();
        }}
      >
        <SearchIcon size={18} strokeWidth={2} className={styles.searchIcon} aria-hidden="true" />
        <input
          className={styles.searchInput}
          placeholder="Rechercher un article ou un membre"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Rechercher un article ou un membre"
        />
      </form>

      <p className={styles.sectionLabel}>Catégories</p>

      {categories === null ? (
        <div className={styles.grid}>
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} height={140} className={styles.tileSkeleton} />
          ))}
        </div>
      ) : (
        <div className={styles.grid}>
          {categories.map((c, i) => {
            const Icon = CATEGORY_ICONS[c.slug] || Tag;
            return (
              <button key={c.id} type="button" className={styles.tile} onClick={() => openCategory(c)}>
                <span className={styles.tileName}>{c.name}</span>
                <Icon
                  size={40}
                  strokeWidth={1.5}
                  className={[styles.tileIcon, styles[ICON_TONES[i % ICON_TONES.length]]].join(" ")}
                  aria-hidden="true"
                />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
