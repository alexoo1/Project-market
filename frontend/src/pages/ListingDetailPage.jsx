import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getListing, createOffer, purchaseListing, startConversation,
} from "../api/endpoints";
import { COLORS, formatFCFA, CONDITION_LABELS, DELIVERY_METHOD_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

export default function ListingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [listing, setListing] = useState(null);
  const [error, setError] = useState(null);
  const [showOffer, setShowOffer] = useState(false);
  const [offerAmount, setOfferAmount] = useState("");
  const [deliveryMethod, setDeliveryMethod] = useState("hand_delivery");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    getListing(id).then(setListing).catch(() => setError("Annonce introuvable."));
  }, [id]);

  const isOwner = user && listing && user.id === listing.seller?.id;

  const handleOffer = async (e) => {
    e.preventDefault();
    if (!user) return navigate("/login");
    setBusy(true);
    setMessage(null);
    try {
      await createOffer(id, Number(offerAmount));
      setMessage({ type: "success", text: "Offre envoyée !" });
      setShowOffer(false);
      setOfferAmount("");
    } catch (err) {
      setMessage({ type: "error", text: err instanceof ApiError ? err.message : "Erreur" });
    } finally {
      setBusy(false);
    }
  };

  const handleBuy = async () => {
    if (!user) return navigate("/login");
    setBusy(true);
    setMessage(null);
    try {
      const order = await purchaseListing(id, { delivery_method: deliveryMethod, payment_method: "mock" });
      navigate(`/orders/${order.id}`);
    } catch (err) {
      setMessage({ type: "error", text: err instanceof ApiError ? err.message : "Erreur" });
    } finally {
      setBusy(false);
    }
  };

  const handleMessage = async () => {
    if (!user) return navigate("/login");
    try {
      const conv = await startConversation(id);
      navigate(`/messages/${conv.id}`);
    } catch (err) {
      setMessage({ type: "error", text: err instanceof ApiError ? err.message : "Erreur" });
    }
  };

  if (error) return <div style={{ padding: 20, color: COLORS.danger }}>{error}</div>;
  if (!listing) return <div style={{ padding: 20, color: COLORS.inkSoft }}>Chargement...</div>;

  return (
    <div style={{ paddingBottom: 100 }}>
      <div style={{ position: "relative", aspectRatio: "4/5", background: "#eee" }}>
        {listing.images?.[0] ? (
          <img
            src={listing.images[0].url}
            alt={listing.title}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: COLORS.inkSoft }}>
            Pas de photo
          </div>
        )}
        <button
          onClick={() => navigate(-1)}
          style={{
            position: "absolute", top: 12, left: 12, width: 36, height: 36, borderRadius: "50%",
            border: "none", background: "rgba(255,255,255,0.9)", cursor: "pointer",
          }}
        >
          ←
        </button>
      </div>

      <div style={{ padding: 16 }}>
        <p style={{ fontSize: 24, fontWeight: 700, margin: 0, color: COLORS.ink }}>{formatFCFA(listing.price)}</p>
        <p style={{ fontSize: 15, margin: "4px 0", color: COLORS.ink }}>{listing.title}</p>
        <p style={{ fontSize: 13, color: COLORS.inkSoft }}>{listing.description}</p>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, margin: "12px 0" }}>
          {[CONDITION_LABELS[listing.condition], listing.size, listing.color].filter(Boolean).map((tag) => (
            <span key={tag} style={{ fontSize: 11.5, padding: "4px 10px", borderRadius: 999, background: COLORS.sandDeep }}>
              {tag}
            </span>
          ))}
        </div>

        <p style={{ fontSize: 12, color: COLORS.inkSoft }}>
          📍 {listing.city} · Statut: {listing.status}
        </p>

        {listing.seller && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "12px 0", borderTop: `1px solid ${COLORS.sandDeep}`, borderBottom: `1px solid ${COLORS.sandDeep}`, margin: "12px 0" }}>
            <div style={{ width: 40, height: 40, borderRadius: "50%", background: COLORS.lagoon, color: COLORS.sand, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 600 }}>
              {listing.seller.display_name?.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p style={{ fontSize: 13.5, fontWeight: 500, margin: 0 }}>{listing.seller.display_name}</p>
              <p style={{ fontSize: 11.5, color: COLORS.inkSoft, margin: 0 }}>
                ⭐ {listing.seller.average_rating} ({listing.seller.review_count} avis)
              </p>
            </div>
          </div>
        )}

        {message && (
          <p style={{ fontSize: 13, color: message.type === "error" ? COLORS.danger : COLORS.lagoon }}>
            {message.text}
          </p>
        )}

        {!isOwner && listing.status === "active" && (
          <>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, color: COLORS.inkSoft }}>Mode de livraison</label>
              <select
                value={deliveryMethod}
                onChange={(e) => setDeliveryMethod(e.target.value)}
                style={{ width: "100%", padding: 10, borderRadius: 12, border: `1px solid ${COLORS.sandDeep}`, marginTop: 4 }}
              >
                {Object.entries(DELIVERY_METHOD_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={handleMessage} style={secondaryBtn}>Message</button>
              <button onClick={() => setShowOffer(true)} style={secondaryBtn}>Faire une offre</button>
              <button onClick={handleBuy} disabled={busy} style={primaryBtn}>Acheter</button>
            </div>
          </>
        )}

        {isOwner && (
          <p style={{ fontSize: 13, color: COLORS.inkSoft, fontStyle: "italic" }}>
            C'est ton annonce.
          </p>
        )}

        {showOffer && (
          <form onSubmit={handleOffer} style={{ marginTop: 16, padding: 16, background: "#fff", borderRadius: 16 }}>
            <p style={{ fontSize: 14, fontWeight: 600, margin: "0 0 8px" }}>Faire une offre</p>
            <input
              type="number"
              placeholder="Montant en FCFA"
              value={offerAmount}
              onChange={(e) => setOfferAmount(e.target.value)}
              required
              style={{ width: "100%", padding: 10, borderRadius: 12, border: `1px solid ${COLORS.sandDeep}`, marginBottom: 8 }}
            />
            <button type="submit" disabled={busy} style={{ ...primaryBtn, width: "100%" }}>
              Envoyer l'offre
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

const primaryBtn = {
  flex: 1, padding: "12px 16px", borderRadius: 999, border: "none",
  background: COLORS.coral, color: "#fff", fontWeight: 600, fontSize: 13.5, cursor: "pointer",
};
const secondaryBtn = {
  flex: 1, padding: "12px 16px", borderRadius: 999, border: `2px solid ${COLORS.lagoon}`,
  background: "transparent", color: COLORS.lagoon, fontWeight: 600, fontSize: 13.5, cursor: "pointer",
};
