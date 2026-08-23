import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, MapPin, MessageCircle, Tag, Pencil, Trash2 } from "lucide-react";
import {
  getListing, createOffer, purchaseListing, startConversation, deleteListing,
} from "../api/endpoints";
import { formatFCFA, CONDITION_LABELS, DELIVERY_METHOD_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import ImageGallery from "../components/ui/ImageGallery";
import IconButton from "../components/ui/IconButton";
import Button from "../components/ui/Button";
import Chip from "../components/ui/Chip";
import Badge from "../components/ui/Badge";
import UserAvatar from "../components/ui/UserAvatar";
import RatingStars from "../components/ui/RatingStars";
import Select from "../components/ui/Select";
import Input from "../components/ui/Input";
import PaymentMethodPicker from "../components/ui/PaymentMethodPicker";
import BottomSheet from "../components/ui/BottomSheet";
import Skeleton from "../components/ui/Skeleton";
import styles from "./ListingDetailPage.module.css";

const STATUS_TONE = { active: "success", sold: "neutral", reserved: "warning", draft: "neutral" };
const STATUS_LABEL = { active: "Disponible", sold: "Vendu", reserved: "Réservé", draft: "Brouillon" };

export default function ListingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [listing, setListing] = useState(null);
  const [error, setError] = useState(null);
  const [showOffer, setShowOffer] = useState(false);
  const [offerAmount, setOfferAmount] = useState("");
  const [showBuy, setShowBuy] = useState(false);
  const [deliveryMethod, setDeliveryMethod] = useState("hand_delivery");
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getListing(id).then(setListing).catch(() => setError("Annonce introuvable."));
  }, [id]);

  const isOwner = user && listing && user.id === listing.seller?.id;

  const handleOffer = async (e) => {
    e.preventDefault();
    if (!user) return navigate("/login");
    setBusy(true);
    try {
      await createOffer(id, Number(offerAmount));
      toast.success("Offre envoyée !");
      setShowOffer(false);
      setOfferAmount("");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  const handleBuy = async () => {
    setBusy(true);
    try {
      const order = await purchaseListing(id, { delivery_method: deliveryMethod, payment_method: paymentMethod });
      navigate(`/orders/${order.id}`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  const openBuySheet = () => {
    if (!user) return navigate("/login");
    setShowBuy(true);
  };

  const handleMessage = async () => {
    if (!user) return navigate("/login");
    try {
      const conv = await startConversation(id);
      navigate(`/messages/${conv.id}`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Supprimer définitivement cette annonce ?")) return;
    setBusy(true);
    try {
      await deleteListing(id);
      toast.success("Annonce supprimée.");
      navigate("/profile");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusy(false);
    }
  };

  if (error) {
    return (
      <div className={styles.page}>
        <IconButton icon={ArrowLeft} label="Retour" variant="solid" onClick={() => navigate(-1)} />
        <p className={styles.errorText}>{error}</p>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className={styles.page}>
        <Skeleton height={480} />
        <div className={styles.body}>
          <Skeleton variant="text" width="40%" height={28} />
          <Skeleton variant="text" width="70%" style={{ marginTop: 10 }} />
          <Skeleton variant="text" width="90%" style={{ marginTop: 16 }} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.heroWrap}>
        <ImageGallery images={listing.images} alt={listing.title} />
        <IconButton
          icon={ArrowLeft}
          label="Retour"
          variant="solid"
          onClick={() => navigate(-1)}
          className={styles.backButton}
        />
      </div>

      <div className={styles.body}>
        <div className={styles.priceRow}>
          <p className={styles.price}>{formatFCFA(listing.price)}</p>
          <Badge tone={STATUS_TONE[listing.status] || "neutral"}>{STATUS_LABEL[listing.status] || listing.status}</Badge>
        </div>
        <p className={styles.title}>{listing.title}</p>

        <div className={styles.tags}>
          {[CONDITION_LABELS[listing.condition], listing.size, listing.color].filter(Boolean).map((tag) => (
            <Chip key={tag}>{tag}</Chip>
          ))}
        </div>

        <p className={styles.location}>
          <MapPin size={14} strokeWidth={2} aria-hidden="true" /> {listing.city}
        </p>

        <p className={styles.description}>{listing.description}</p>

        {listing.seller && (
          <Link to={`/users/${listing.seller.id}`} className={styles.sellerRow}>
            <UserAvatar name={listing.seller.display_name} src={listing.seller.profile_photo_url} />
            <div>
              <p className={styles.sellerName}>{listing.seller.display_name}</p>
              <div className={styles.sellerRating}>
                <RatingStars value={listing.seller.average_rating} size={13} />
                <span>({listing.seller.review_count})</span>
              </div>
            </div>
          </Link>
        )}

        {isOwner && (
          <div className={styles.ownerActions}>
            <Button variant="secondary" onClick={() => navigate(`/sell/${id}`)}>
              <Pencil size={15} strokeWidth={2} /> Modifier
            </Button>
            <Button variant="danger" onClick={handleDelete} loading={busy}>
              <Trash2 size={15} strokeWidth={2} /> Supprimer
            </Button>
          </div>
        )}
      </div>

      {!isOwner && listing.status === "active" && (
        <div className={styles.actionBar}>
          <IconButton icon={MessageCircle} label="Envoyer un message" variant="solid" onClick={handleMessage} />
          <Button variant="secondary" onClick={() => setShowOffer(true)} className={styles.offerButton}>
            <Tag size={15} strokeWidth={2} /> Faire une offre
          </Button>
          <Button variant="primary" onClick={openBuySheet} className={styles.buyButton}>
            Acheter
          </Button>
        </div>
      )}

      <BottomSheet open={showOffer} onClose={() => setShowOffer(false)} title="Faire une offre">
        <form onSubmit={handleOffer} className={styles.offerForm}>
          <Input
            type="number"
            placeholder="Montant en FCFA"
            value={offerAmount}
            onChange={(e) => setOfferAmount(e.target.value)}
            required
          />
          <Button type="submit" loading={busy} fullWidth>
            Envoyer l'offre
          </Button>
        </form>
      </BottomSheet>

      <BottomSheet open={showBuy} onClose={() => setShowBuy(false)} title="Finaliser l'achat">
        <div className={styles.buySheet}>
          <Select label="Mode de livraison" value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)}>
            {Object.entries(DELIVERY_METHOD_LABELS).map(([val, label]) => (
              <option key={val} value={val}>{label}</option>
            ))}
          </Select>
          <PaymentMethodPicker value={paymentMethod} onChange={setPaymentMethod} />
          <div className={styles.buyTotalRow}>
            <span>Total</span>
            <strong>{formatFCFA(listing.price)}</strong>
          </div>
          <Button onClick={handleBuy} loading={busy} fullWidth size="lg">
            Confirmer l'achat
          </Button>
        </div>
      </BottomSheet>
    </div>
  );
}
