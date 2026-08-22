import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getMyPurchases, getMySales, getFavorites, getMyListings } from "../api/endpoints";
import { COLORS, formatFCFA, ORDER_STATUS_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import ListingCard from "../components/ListingCard";

const TABS = ["Achats", "Ventes", "Favoris", "Mes annonces"];

export default function ProfilePage() {
  const { user, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("Achats");
  const [purchases, setPurchases] = useState([]);
  const [sales, setSales] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [myListings, setMyListings] = useState([]);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/login");
      return;
    }
    if (user) {
      getMyPurchases().then(setPurchases).catch(() => {});
      getMySales().then(setSales).catch(() => {});
      getFavorites().then(setFavorites).catch(() => {});
      getMyListings().then(setMyListings).catch(() => {});
    }
  }, [user, authLoading, navigate]);

  if (!user) return null;

  return (
    <div style={{ padding: "20px 16px 90px" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", marginBottom: 16 }}>
        <div style={{ width: 72, height: 72, borderRadius: "50%", background: COLORS.lagoon, color: COLORS.sand, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, fontWeight: 700 }}>
          {user.display_name?.slice(0, 2).toUpperCase()}
        </div>
        <p style={{ fontWeight: 700, fontSize: 17, margin: "10px 0 0" }}>{user.display_name}</p>
        <p style={{ fontSize: 12.5, color: COLORS.inkSoft, margin: "2px 0" }}>
          ⭐ {user.average_rating} · {user.review_count} avis · {user.city}
        </p>
        <button
          onClick={logout}
          style={{ marginTop: 8, fontSize: 12, color: COLORS.danger, background: "none", border: "none", cursor: "pointer" }}
        >
          Se déconnecter
        </button>
      </div>

      <div style={{ display: "flex", gap: 6, overflowX: "auto", marginBottom: 16 }}>
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              flexShrink: 0, padding: "6px 14px", borderRadius: 999, border: "none", fontSize: 12.5, cursor: "pointer",
              background: tab === t ? COLORS.coral : "#fff", color: tab === t ? "#fff" : COLORS.ink,
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Achats" && <OrderList orders={purchases} role="buyer" />}
      {tab === "Ventes" && <OrderList orders={sales} role="seller" />}
      {tab === "Favoris" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
          {favorites.map((l) => <ListingCard key={l.id} listing={l} />)}
          {favorites.length === 0 && <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Aucun favori.</p>}
        </div>
      )}
      {tab === "Mes annonces" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px 12px" }}>
          {myListings.map((l) => <ListingCard key={l.id} listing={l} />)}
          {myListings.length === 0 && <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Aucune annonce.</p>}
        </div>
      )}
    </div>
  );
}

function OrderList({ orders, role }) {
  if (orders.length === 0) return <p style={{ color: COLORS.inkSoft, fontSize: 13 }}>Aucune commande.</p>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {orders.map((o) => (
        <Link
          key={o.id}
          to={`/orders/${o.id}`}
          style={{
            display: "flex", justifyContent: "space-between", padding: 14, background: "#fff",
            borderRadius: 14, textDecoration: "none", color: "inherit",
          }}
        >
          <div>
            <p style={{ margin: 0, fontSize: 13.5, fontWeight: 600 }}>{formatFCFA(o.total)}</p>
            <p style={{ margin: "2px 0 0", fontSize: 11.5, color: COLORS.inkSoft }}>
              {ORDER_STATUS_LABELS[o.status] || o.status}
            </p>
          </div>
          <span style={{ fontSize: 11, color: COLORS.inkSoft, alignSelf: "center" }}>
            {role === "buyer" ? "Achat" : "Vente"}
          </span>
        </Link>
      ))}
    </div>
  );
}
