import { useEffect, useState } from "react";
import { Search as SearchIcon, SlidersHorizontal, SearchX } from "lucide-react";
import { searchListings } from "../api/endpoints";
import ListingCard, { ListingCardSkeleton } from "../components/ListingCard";
import SearchInput from "../components/ui/SearchInput";
import FilterChip from "../components/ui/FilterChip";
import BottomSheet from "../components/ui/BottomSheet";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import styles from "./SearchPage.module.css";

const SORT_LABELS = { recent: "Nouveautés", price_asc: "Prix croissant", price_desc: "Prix décroissant" };

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [city, setCity] = useState("");
  const [sort, setSort] = useState("recent");
  const [listings, setListings] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);

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

  const applyFilters = () => {
    setSheetOpen(false);
    runSearch();
  };

  const activeFilterCount = [priceMin, priceMax, city].filter(Boolean).length;

  return (
    <div className={styles.page}>
      <div className={styles.searchRow}>
        <SearchInput
          placeholder="Rechercher un article, une marque..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          onClear={() => setQ("")}
        />
      </div>

      <div className={styles.chipsRow}>
        <FilterChip icon={SlidersHorizontal} active={activeFilterCount > 0} onClick={() => setSheetOpen(true)}>
          Filtres{activeFilterCount > 0 ? ` (${activeFilterCount})` : ""}
        </FilterChip>
        <FilterChip active onClick={() => setSheetOpen(true)}>
          {SORT_LABELS[sort]}
        </FilterChip>
      </div>

      {loading ? (
        <div className={styles.grid}>
          {Array.from({ length: 6 }).map((_, i) => (
            <ListingCardSkeleton key={i} />
          ))}
        </div>
      ) : listings.length === 0 ? (
        <EmptyState icon={SearchX} title="Aucun résultat" description="Essaie d'autres mots-clés ou ajuste tes filtres." />
      ) : (
        <>
          <p className={styles.total}>{total} résultat{total > 1 ? "s" : ""}</p>
          <div className={styles.grid}>
            {listings.map((l) => (
              <ListingCard key={l.id} listing={l} />
            ))}
          </div>
        </>
      )}

      <BottomSheet open={sheetOpen} onClose={() => setSheetOpen(false)} title="Filtres">
        <div className={styles.sheetForm}>
          <div className={styles.priceRange}>
            <Input placeholder="Prix min" type="number" value={priceMin} onChange={(e) => setPriceMin(e.target.value)} />
            <Input placeholder="Prix max" type="number" value={priceMax} onChange={(e) => setPriceMax(e.target.value)} />
          </div>
          <Input placeholder="Ville" value={city} onChange={(e) => setCity(e.target.value)} />
          <Select label="Trier par" value={sort} onChange={(e) => setSort(e.target.value)}>
            {Object.entries(SORT_LABELS).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </Select>
          <Button fullWidth size="lg" onClick={applyFilters}>
            <SearchIcon size={16} strokeWidth={2} /> Appliquer
          </Button>
        </div>
      </BottomSheet>
    </div>
  );
}
