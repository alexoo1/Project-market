import { useEffect, useState } from "react";
import { getCategories, searchListings } from "../api/endpoints";
import ListingCard from "../components/ListingCard";
import { COLORS } from "../theme";
import { useAuth } from "../context/AuthContext";

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
    <div style={{ padding: "16px 16px 80px" }}>
      <div style={{ marginBottom: 16 }}>
        {user && <p style={{ fontSize: 11, color: COLORS.inkSoft, margin: 0 }}>{user.city || "Côte d'Ivoire"}</p>}
        <h1 style={{ fontSize: 22, fontWeight: 700, color: COLORS.lagoon, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
          Project Market
        </h1>
      </div>

      <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 8, marginBottom: 16 }}>
        <CategoryChip label="Tout" active={!activeCategory} onClick={() => setActiveCategory(null)} />
        {categories.map((c) => (
          <CategoryChip
            key={c.id}
            label={c.name}
            active={activeCategory === c.id}
            onClick={() => setActiveCategory(c.id)}
          />
        ))}
      </div>

      {loading && <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Chargement...</p>}
      {error && <p style={{ color: COLORS.danger, fontSize: 13 }}>{error}</p>}

      {!loading && !error && listings.length === 0 && (
        <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Aucune annonce pour le moment.</p>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
        {listings.map((l) => (
          <ListingCard key={l.id} listing={l} />
        ))}
      </div>
    </div>
  );
}

function CategoryChip({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        flexShrink: 0,
        fontSize: 12.5,
        fontWeight: 500,
        padding: "6px 14px",
        borderRadius: 999,
        border: "none",
        cursor: "pointer",
        background: active ? COLORS.coral : "#fff",
        color: active ? COLORS.sand : COLORS.ink,
      }}
    >
      {label}
    </button>
  );
}
