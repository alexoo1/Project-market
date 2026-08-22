import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getOrder, payOrder, shipOrder, confirmReceipt, cancelOrder, createReview } from "../api/endpoints";
import { COLORS, formatFCFA, ORDER_STATUS_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

export default function OrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reviewDone, setReviewDone] = useState(false);

  const load = () => getOrder(id).then(setOrder).catch(() => setError("Commande introuvable."));

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/login");
      return;
    }
    if (user) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, user, authLoading]);

  if (error) return <div style={{ padding: 20, color: COLORS.danger }}>{error}</div>;
  if (!order) return <div style={{ padding: 20, color: COLORS.inkSoft }}>Chargement...</div>;

  const isBuyer = user?.id === order.buyer_id;
  const isSeller = user?.id === order.seller_id;

  const runAction = async (fn) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  const handleReview = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await createReview(id, rating, comment || undefined);
      setReviewDone(true);
      setShowReview(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: "20px 16px 80px", maxWidth: 480, margin: "0 auto" }}>
      <h1 style={{ fontSize: 18, fontWeight: 700, color: COLORS.lagoon }}>Commande</h1>

      <div style={{ background: "#fff", borderRadius: 16, padding: 16, marginTop: 12 }}>
        <Row label="Statut" value={ORDER_STATUS_LABELS[order.status] || order.status} strong />
        <Row label="Prix article" value={formatFCFA(order.item_price)} />
        <Row label="Frais plateforme" value={formatFCFA(order.platform_fee)} />
        <Row label="Livraison" value={formatFCFA(order.delivery_fee)} />
        <Row label="Total" value={formatFCFA(order.total)} strong />
        {order.delivery?.tracking_number && (
          <Row label="Suivi" value={order.delivery.tracking_number} />
        )}
      </div>

      {error && <p style={{ color: COLORS.danger, fontSize: 13, marginTop: 12 }}>{error}</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 16 }}>
        {isBuyer && order.status === "pending_payment" && (
          <>
            <button onClick={() => runAction(() => payOrder(id))} disabled={busy} style={primaryBtn}>
              Payer maintenant (paiement mock)
            </button>
            <button onClick={() => runAction(() => cancelOrder(id))} disabled={busy} style={dangerBtn}>
              Annuler la commande
            </button>
          </>
        )}

        {isSeller && order.status === "paid" && (
          <button onClick={() => runAction(() => shipOrder(id))} disabled={busy} style={primaryBtn}>
            Marquer comme expédiée
          </button>
        )}

        {isBuyer && order.status === "shipped" && (
          <button onClick={() => runAction(() => confirmReceipt(id))} disabled={busy} style={primaryBtn}>
            Confirmer la réception
          </button>
        )}

        {order.status === "completed" && !reviewDone && !showReview && (
          <button onClick={() => setShowReview(true)} style={primaryBtn}>
            Laisser un avis
          </button>
        )}
        {reviewDone && <p style={{ color: COLORS.lagoon, fontSize: 13 }}>Merci pour ton avis !</p>}
      </div>

      {showReview && (
        <form onSubmit={handleReview} style={{ marginTop: 16, background: "#fff", borderRadius: 16, padding: 16 }}>
          <p style={{ fontWeight: 600, fontSize: 14, margin: "0 0 8px" }}>Ton avis</p>
          <select value={rating} onChange={(e) => setRating(Number(e.target.value))} style={{ width: "100%", padding: 10, borderRadius: 10, marginBottom: 8 }}>
            {[5, 4, 3, 2, 1].map((r) => <option key={r} value={r}>{"⭐".repeat(r)}</option>)}
          </select>
          <textarea
            placeholder="Commentaire (facultatif)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            style={{ width: "100%", padding: 10, borderRadius: 10, marginBottom: 8, resize: "vertical" }}
          />
          <button type="submit" disabled={busy} style={primaryBtn}>Envoyer l'avis</button>
        </form>
      )}
    </div>
  );
}

function Row({ label, value, strong }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", padding: "6px 0" }}>
      <span style={{ fontSize: 13, color: COLORS.inkSoft }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: strong ? 700 : 400, color: COLORS.ink }}>{value}</span>
    </div>
  );
}

const primaryBtn = {
  padding: "12px 16px", borderRadius: 999, border: "none",
  background: COLORS.coral, color: "#fff", fontWeight: 600, fontSize: 13.5, cursor: "pointer",
};
const dangerBtn = {
  padding: "12px 16px", borderRadius: 999, border: `1px solid ${COLORS.danger}`,
  background: "transparent", color: COLORS.danger, fontWeight: 600, fontSize: 13.5, cursor: "pointer",
};
