import { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import {
  ArrowLeft, Search as SearchIcon, ChevronRight, Grid3x3,
  Shirt, Footprints, ShoppingBag, Gem, Sparkles, Watch, Glasses,
  Baby, Backpack, Luggage, Dumbbell, Zap, Crown, Tag,
  Lamp, UtensilsCrossed, Archive, Trees, Smartphone, Laptop,
  Headphones, Gamepad2, Camera, BookOpen, Film, Music, Dices,
  Palette, Bike,
} from "lucide-react";
import { getCategories } from "../api/endpoints";
import IconButton from "../components/ui/IconButton";
import Skeleton from "../components/ui/Skeleton";
import styles from "./CategoryDetailPage.module.css";

const KEYWORD_ICONS = [
  [["t-shirt", "vetement", "veste", "pantalon", "jogger"], Shirt],
  [["chaussure", "basket", "sandale", "mocassin", "botte", "talon"], Footprints],
  [["running", "skate"], Zap],
  [["basketball", "sport"], Dumbbell],
  [["fitness", "musculation"], Dumbbell],
  [["velo"], Bike],
  [["sac a dos"], Backpack],
  [["valise"], Luggage],
  [["sac"], ShoppingBag],
  [["bijou"], Gem],
  [["montre"], Watch],
  [["lunette"], Glasses],
  [["beaute", "soin"], Sparkles],
  [["jouet", "puericulture", "fille", "garcon"], Baby],
  [["edition limitee", "lifestyle"], Crown],
  [["decoration"], Lamp],
  [["cuisine"], UtensilsCrossed],
  [["rangement"], Archive],
  [["jardin"], Trees],
  [["telephone"], Smartphone],
  [["ordinateur", "tablette"], Laptop],
  [["audio", "casque"], Headphones],
  [["console", "jeu video"], Gamepad2],
  [["photo", "camera"], Camera],
  [["livre", "manga", "bd"], BookOpen],
  [["film", "serie"], Film],
  [["musique", "instrument"], Music],
  [["jeu de societe"], Dices],
  [["art", "collection", "loisir creatif"], Palette],
];

function normalize(str) {
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "");
}

function iconFor(name) {
  const normalized = normalize(name);
  for (const [keywords, Icon] of KEYWORD_ICONS) {
    if (keywords.some((kw) => normalized.includes(kw))) return Icon;
  }
  return Tag;
}

export default function CategoryDetailPage() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [categories, setCategories] = useState(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  const parent = categories?.find((c) => c.id === id) || (
    location.state?.categoryName ? { id, name: location.state.categoryName } : null
  );
  const children = categories?.filter((c) => c.parent_id === id) || [];

  const openSearch = (categoryId, categoryName) => {
    navigate("/search", { state: { categoryId, categoryName } });
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <IconButton icon={ArrowLeft} label="Retour" onClick={() => navigate(-1)} />
        <p className={styles.headerTitle}>{parent?.name || ""}</p>
        <IconButton icon={SearchIcon} label="Rechercher" onClick={() => openSearch(id, parent?.name)} />
      </div>

      {categories === null ? (
        <div className={styles.list}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className={styles.row}>
              <Skeleton variant="circle" width={32} height={32} />
              <Skeleton variant="text" width="60%" />
            </div>
          ))}
        </div>
      ) : (
        <div className={styles.list}>
          <button
            type="button"
            className={styles.row}
            onClick={() => openSearch(id, parent?.name)}
          >
            <span className={styles.rowIcon}>
              <Grid3x3 size={18} strokeWidth={1.75} />
            </span>
            <span className={styles.rowName}>Tous</span>
            <ChevronRight size={18} strokeWidth={1.75} className={styles.chevron} aria-hidden="true" />
          </button>

          {children.map((c) => {
            const Icon = iconFor(c.name);
            return (
              <button
                key={c.id}
                type="button"
                className={styles.row}
                onClick={() => openSearch(c.id, c.name)}
              >
                <span className={styles.rowIcon}>
                  <Icon size={18} strokeWidth={1.75} />
                </span>
                <span className={styles.rowName}>{c.name}</span>
                <ChevronRight size={18} strokeWidth={1.75} className={styles.chevron} aria-hidden="true" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
