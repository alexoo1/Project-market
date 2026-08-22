import { useEffect, useState } from "react";
import { searchListings } from "../api/endpoints";
import ListingCard from "../components/ListingCard";
import { COLORS } from "../theme";
import { inputStyle } from "./LoginPage";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [city, setCity] = useState("");
  const [sort, setSort] = useState("recent");
  const [listings, setListings] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const runSearch = () => {
    setLoading(true);
    searchListings({
      q: q || undefined,
      price_min: priceMin || undefined,
      price_max: priceMax || undefined,
      city: city || undefined,
      sort,
      page_size: 20,
    })
      .then((data) => {
        setListings(data.items);
        setTotal(data.total);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ padding: "16px 16px 80px" }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <input
          placeholder="Rechercher un article, une marque..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          style={{ ...inputStyle, flex: 1, background: "#fff" }}
        />
        <button
          onClick={runSearch}
          style={{
            width: 44, borderRadius: 22, border: "none", background: COLORS.lagoon, color: COLORS.sand,
            cursor: "pointer",
          }}
        >
          🔍
        </button>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        <input
          placeholder="Prix min"
          type="number"
          value={priceMin}
          onChange={(e) => setPriceMin(e.target.value)}
          style={{ ...inputStyle, width: 100, background: "#fff", padding: "8px 12px" }}
        />
        <input
          placeholder="Prix max"
          type="number"
          value={priceMax}
          onChange={(e) => setPriceMax(e.target.value)}
          style={{ ...inputStyle, width: 100, background: "#fff", padding: "8px 12px" }}
        />
        <input
          placeholder="Ville"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          style={{ ...inputStyle, width: 120, background: "#fff", padding: "8px 12px" }}
        />
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          style={{ ...inputStyle, background: "#fff", padding: "8px 12px" }}
        >
          <option value="recent">Nouveautés</option>
          <option value="price_asc">Prix croissant</option>
          <option value="price_desc">Prix décroissant</option>
        </select>
        <button onClick={runSearch} style={{ ...inputStyle, background: COLORS.coral, color: "#fff", border: "none", cursor: "pointer" }}>
          Filtrer
        </button>
      </div>

      {loading ? (
        <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Recherche...</p>
      ) : (
        <>
          <p style={{ color: COLORS.inkSoft, fontSize: 12, marginBottom: 12 }}>{total} résultat(s)</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
            {listings.map((l) => (
              <ListingCard key={l.id} listing={l} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
