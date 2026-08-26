import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getOrder, payOrder, shipOrder, confirmReceipt, cancelOrder, createReview } from "../api/endpoints";
import { formatFCFA, ORDER_STATUS_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import RatingStars from "../components/ui/RatingStars";
import Skeleton from "../components/ui/Skeleton";
import styles from "./OrderDetailPage.module.css";

const STATUS_TONE = {
  completed: "success", cancelled: "danger", disputed: "danger", refunded: "neutral",
  paid: "info", shipped: "info", pending_payment: "warning",
};

export default function OrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const toast = useToast();
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

  if (error) return <div className={styles.errorPage}>{error}</div>;
  if (!order) {
    return (
      <div className={styles.page}>
        <Skeleton height={160} />
      </div>
    );
  }

  const isBuyer = user?.id === order.buyer_id;
  const isSeller = user?.id === order.seller_id;

  const runAction = async (fn) => {
    setBusy(true);
    try {
      await fn();
      await load();
      toast.success("Mise à jour effectuée.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
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
      toast.success("Merci pour ton avis !");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Commande</h1>

      <div className={styles.card}>
        <Row label="Statut" value={<Badge tone={STATUS_TONE[order.status] || "neutral"}>{ORDER_STATUS_LABELS[order.status] || order.status}</Badge>} />
        <Row label="Prix article" value={formatFCFA(order.item_price)} />
        <Row label="Frais plateforme" value={formatFCFA(order.platform_fee)} />
        <Row label="Livraison" value={formatFCFA(order.delivery_fee)} />
        <Row label="Total" value={formatFCFA(order.total)} strong />
        {order.delivery?.carrier && <Row label="Transporteur" value={order.delivery.carrier} />}
        {order.delivery?.tracking_number && <Row label="Suivi" value={order.delivery.tracking_number} />}
      </div>

      <div className={styles.actions}>
        {isBuyer && order.status === "pending_payment" && (
          <>
            <Button fullWidth onClick={() => runAction(() => payOrder(id))} loading={busy}>
              Payer maintenant (paiement mock)
            </Button>
            <Button fullWidth variant="danger" onClick={() => runAction(() => cancelOrder(id))} disabled={busy}>
              Annuler la commande
            </Button>
          </>
        )}

        {isSeller && order.status === "paid" && (
          <Button fullWidth onClick={() => runAction(() => shipOrder(id))} loading={busy}>
            Marquer comme expédiée
          </Button>
        )}

        {isBuyer && order.status === "shipped" && (
          <Button fullWidth onClick={() => runAction(() => confirmReceipt(id))} loading={busy}>
            Confirmer la réception
          </Button>
        )}

        {order.status === "completed" && !reviewDone && !showReview && (
          <Button fullWidth onClick={() => setShowReview(true)}>
            Laisser un avis
          </Button>
        )}
        {reviewDone && <p className={styles.thanks}>Merci pour ton avis !</p>}
      </div>

      {showReview && (
        <form onSubmit={handleReview} className={styles.reviewCard}>
          <p className={styles.reviewTitle}>Ton avis</p>
          <RatingStars value={rating} interactive size={20} onChange={setRating} />
          <textarea
            placeholder="Commentaire (facultatif)"
            aria-label="Commentaire (facultatif)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            className={styles.textarea}
          />
          <Button type="submit" loading={busy} fullWidth>Envoyer l'avis</Button>
        </form>
      )}
    </div>
  );
}

function Row({ label, value, strong }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={[styles.rowValue, strong ? styles.rowValueStrong : ""].filter(Boolean).join(" ")}>{value}</span>
    </div>
  );
}
