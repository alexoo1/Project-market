import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { LogOut, MapPin, Calendar, ShoppingBag, Heart, Tag, Package, Wallet as WalletIcon, ArrowDownCircle, ArrowUpCircle, HandCoins, Pencil } from "lucide-react";
import {
  getMyPurchases, getMySales, getFavorites, getMyListings, getWallet, requestWithdrawal,
  getMyOffers, acceptOffer, rejectOffer, counterOffer,
} from "../api/endpoints";
import { formatFCFA, ORDER_STATUS_LABELS, WALLET_TRANSACTION_LABELS, OFFER_STATUS_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import ListingCard, { ListingCardSkeleton } from "../components/ListingCard";
import UserAvatar from "../components/ui/UserAvatar";
import RatingStars from "../components/ui/RatingStars";
import Chip from "../components/ui/Chip";
import Badge from "../components/ui/Badge";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import PaymentMethodPicker from "../components/ui/PaymentMethodPicker";
import BottomSheet from "../components/ui/BottomSheet";
import styles from "./ProfilePage.module.css";

const TABS = [
  { key: "purchases", label: "Achats" },
  { key: "sales", label: "Ventes" },
  { key: "offers", label: "Offres" },
  { key: "favorites", label: "Favoris" },
  { key: "listings", label: "Mes annonces" },
  { key: "wallet", label: "Portefeuille" },
];

const ORDER_STATUS_TONE = {
  completed: "success", cancelled: "danger", disputed: "danger", refunded: "neutral",
};

const OFFER_STATUS_TONE = {
  pending: "warning", accepted: "success", rejected: "danger", countered: "info",
  expired: "neutral", purchased: "success",
};

export default function ProfilePage() {
  const { user, loading: authLoading, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("purchases");
  const [purchases, setPurchases] = useState(null);
  const [sales, setSales] = useState(null);
  const [favorites, setFavorites] = useState(null);
  const [myListings, setMyListings] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [offers, setOffers] = useState(null);

  const loadWallet = () => getWallet().then(setWallet).catch(() => setWallet({ balance: 0, transactions: [] }));
  const loadOffers = () => getMyOffers().then(setOffers).catch(() => setOffers([]));

  useEffect(() => {
    if (!authLoading && !user) {
      navigate("/login");
      return;
    }
    if (user) {
      getMyPurchases().then(setPurchases).catch(() => setPurchases([]));
      getMySales().then(setSales).catch(() => setSales([]));
      getFavorites().then(setFavorites).catch(() => setFavorites([]));
      getMyListings().then(setMyListings).catch(() => setMyListings([]));
      loadWallet();
      loadOffers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, authLoading, navigate]);

  if (!user) return null;

  return (
    <div className={styles.page}>
      <div className={styles.profileHeader}>
        <UserAvatar name={user.display_name} src={user.profile_photo_url} size="lg" />
        <p className={styles.name}>{user.display_name}</p>
        <div className={styles.metaRow}>
          <RatingStars value={user.average_rating} size={13} />
          <span>({user.review_count})</span>
        </div>
        <div className={styles.trustRow}>
          {user.city && (
            <span className={styles.trustItem}><MapPin size={13} strokeWidth={1.75} /> {user.city}</span>
          )}
          <span className={styles.trustItem}>
            <Calendar size={13} strokeWidth={1.75} /> Membre depuis {new Date(user.created_at).getFullYear()}
          </span>
        </div>
        <div className={styles.headerActions}>
          <Button variant="secondary" onClick={() => navigate("/profile/edit")}>
            <Pencil size={20} strokeWidth={1.75} /> Modifier le profil
          </Button>
        </div>
        <button onClick={logout} className={styles.logout}>
          <LogOut size={14} strokeWidth={1.75} /> Se déconnecter
        </button>
      </div>

      <div className={styles.tabs}>
        {TABS.map((t) => (
          <Chip key={t.key} active={tab === t.key} onClick={() => setTab(t.key)}>
            {t.label}
          </Chip>
        ))}
      </div>

      <div className={styles.tabContent}>
        {tab === "purchases" && <OrderList orders={purchases} role="buyer" />}
        {tab === "sales" && <OrderList orders={sales} role="seller" />}
        {tab === "offers" && <OffersTab offers={offers} userId={user.id} onChanged={loadOffers} />}
        {tab === "favorites" && <ListingGrid items={favorites} allFavorited emptyIcon={Heart} emptyTitle="Aucun favori" emptyDescription="Les annonces que tu aimes apparaîtront ici." />}
        {tab === "listings" && <ListingGrid items={myListings} emptyIcon={Tag} emptyTitle="Aucune annonce" emptyDescription="Publie ton premier article pour le voir ici." />}
        {tab === "wallet" && <WalletTab wallet={wallet} onChanged={loadWallet} />}
      </div>
    </div>
  );
}

function WalletTab({ wallet, onChanged }) {
  const toast = useToast();
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [method, setMethod] = useState("card");
  const [destination, setDestination] = useState("");
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);

  if (!wallet) {
    return (
      <div className={styles.walletCard}>
        <Skeleton variant="text" width="50%" height={32} />
      </div>
    );
  }

  const handleWithdraw = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await requestWithdrawal({ method, destination, amount: Number(amount) });
      toast.success("Retrait effectué !");
      setShowWithdraw(false);
      setDestination("");
      setAmount("");
      onChanged();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors du retrait.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className={styles.walletCard}>
        <p className={styles.walletLabel}>Solde disponible</p>
        <p className={styles.walletBalance}>{formatFCFA(wallet.balance)}</p>
        <Button disabled={wallet.balance <= 0} onClick={() => setShowWithdraw(true)} fullWidth>
          Retirer
        </Button>
      </div>

      {wallet.transactions.length === 0 ? (
        <EmptyState
          icon={WalletIcon}
          title="Aucun mouvement"
          description="Les ventes que tu confirmes apparaîtront ici, une fois l'acheteur satisfait."
        />
      ) : (
        <div className={styles.orderList}>
          {wallet.transactions.map((t) => {
            const isCredit = t.type === "sale_credit";
            return (
              <div key={t.id} className={styles.transactionRow}>
                <div className={[styles.orderIcon, isCredit ? styles.creditIcon : ""].filter(Boolean).join(" ")}>
                  {isCredit ? (
                    <ArrowDownCircle size={20} strokeWidth={1.75} />
                  ) : (
                    <ArrowUpCircle size={20} strokeWidth={1.75} />
                  )}
                </div>
                <div className={styles.orderInfo}>
                  <div>
                    <p className={styles.orderPrice}>{WALLET_TRANSACTION_LABELS[t.type] || t.type}</p>
                    {t.withdrawal_destination && (
                      <p className={styles.transactionMeta}>{t.withdrawal_destination}</p>
                    )}
                  </div>
                  <p className={[styles.transactionAmount, isCredit ? styles.creditText : ""].filter(Boolean).join(" ")}>
                    {isCredit ? "+" : "-"}{formatFCFA(t.amount)}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <BottomSheet open={showWithdraw} onClose={() => setShowWithdraw(false)} title="Retirer des fonds">
        <form onSubmit={handleWithdraw} className={styles.withdrawForm}>
          <PaymentMethodPicker value={method} onChange={setMethod} label="Destination" />
          <Input
            placeholder={method === "card" ? "Numéro de carte" : "Numéro de téléphone"}
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            required
          />
          <Input
            type="number"
            placeholder="Montant en FCFA"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            max={wallet.balance}
            required
          />
          <p className={styles.walletHint}>Solde disponible : {formatFCFA(wallet.balance)}</p>
          <Button type="submit" loading={busy} fullWidth>
            Confirmer le retrait
          </Button>
        </form>
      </BottomSheet>
    </>
  );
}

function OffersTab({ offers, userId, onChanged }) {
  const toast = useToast();
  const [busyId, setBusyId] = useState(null);
  const [counterFor, setCounterFor] = useState(null);
  const [counterAmount, setCounterAmount] = useState("");

  if (offers === null) {
    return (
      <div className={styles.orderList}>
        {Array.from({ length: 3 }).map((_, i) => <div key={i} className={styles.orderSkeleton} />)}
      </div>
    );
  }
  if (offers.length === 0) {
    return <EmptyState icon={HandCoins} title="Aucune offre" description="Les offres que tu envoies ou reçois apparaîtront ici." />;
  }

  const run = async (offerId, fn) => {
    setBusyId(offerId);
    try {
      await fn();
      onChanged();
      toast.success("Offre mise à jour.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setBusyId(null);
    }
  };

  const submitCounter = async (e) => {
    e.preventDefault();
    await run(counterFor, () => counterOffer(counterFor, Number(counterAmount)));
    setCounterFor(null);
    setCounterAmount("");
  };

  return (
    <>
      <div className={styles.orderList}>
        {offers.map((o) => {
          const isSeller = o.seller_id === userId;
          const canRespond = o.status === "pending" && (
            (o.proposed_by === "buyer" && isSeller) || (o.proposed_by === "seller" && !isSeller)
          );
          return (
            <div key={o.id} className={styles.offerRow}>
              <div className={styles.orderInfo}>
                <div>
                  <p className={styles.orderPrice}>{o.listing?.title || "Annonce"}</p>
                  <p className={styles.transactionMeta}>{formatFCFA(o.amount)} · {isSeller ? "Reçue" : "Envoyée"}</p>
                </div>
                <Badge tone={OFFER_STATUS_TONE[o.status] || "neutral"}>{OFFER_STATUS_LABELS[o.status] || o.status}</Badge>
              </div>
              {canRespond && (
                <div className={styles.offerActions}>
                  <Button size="md" variant="danger" disabled={busyId === o.id} onClick={() => run(o.id, () => rejectOffer(o.id))}>
                    Refuser
                  </Button>
                  <Button size="md" variant="secondary" disabled={busyId === o.id} onClick={() => setCounterFor(o.id)}>
                    Contre-offre
                  </Button>
                  <Button size="md" loading={busyId === o.id} onClick={() => run(o.id, () => acceptOffer(o.id))}>
                    Accepter
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <BottomSheet open={!!counterFor} onClose={() => setCounterFor(null)} title="Faire une contre-offre">
        <form onSubmit={submitCounter} className={styles.withdrawForm}>
          <Input
            type="number"
            placeholder="Montant en FCFA"
            value={counterAmount}
            onChange={(e) => setCounterAmount(e.target.value)}
            required
          />
          <Button type="submit" loading={busyId === counterFor} fullWidth>
            Envoyer la contre-offre
          </Button>
        </form>
      </BottomSheet>
    </>
  );
}

function ListingGrid({ items, allFavorited = false, emptyIcon, emptyTitle, emptyDescription }) {
  if (items === null) {
    return (
      <div className={styles.grid}>
        {Array.from({ length: 4 }).map((_, i) => <ListingCardSkeleton key={i} />)}
      </div>
    );
  }
  if (items.length === 0) {
    return <EmptyState icon={emptyIcon} title={emptyTitle} description={emptyDescription} />;
  }
  return (
    <div className={styles.grid}>
      {items.map((l) => <ListingCard key={l.id} listing={l} isFavorited={allFavorited} />)}
    </div>
  );
}

function OrderList({ orders, role }) {
  if (orders === null) {
    return (
      <div className={styles.orderList}>
        {Array.from({ length: 3 }).map((_, i) => <div key={i} className={styles.orderSkeleton} />)}
      </div>
    );
  }
  if (orders.length === 0) {
    return <EmptyState icon={ShoppingBag} title="Aucune commande" description={role === "buyer" ? "Tes achats apparaîtront ici." : "Tes ventes apparaîtront ici."} />;
  }
  return (
    <div className={styles.orderList}>
      {orders.map((o) => (
        <Link key={o.id} to={`/orders/${o.id}`} className={styles.orderRow}>
          <div className={styles.orderIcon}>
            <Package size={20} strokeWidth={1.75} />
          </div>
          <div className={styles.orderInfo}>
            <p className={styles.orderPrice}>{formatFCFA(o.total)}</p>
            <Badge tone={ORDER_STATUS_TONE[o.status] || "info"}>{ORDER_STATUS_LABELS[o.status] || o.status}</Badge>
          </div>
        </Link>
      ))}
    </div>
  );
}
