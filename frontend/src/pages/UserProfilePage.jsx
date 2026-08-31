import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { MapPin, Calendar, Tag, MessageSquare } from "lucide-react";
import {
  getUserProfile, searchListings, getUserReviews, followUser, unfollowUser, getFollowStatus,
} from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import UserAvatar from "../components/ui/UserAvatar";
import RatingStars from "../components/ui/RatingStars";
import Button from "../components/ui/Button";
import Chip from "../components/ui/Chip";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import ListingCard, { ListingCardSkeleton } from "../components/ListingCard";
import { formatRelativeTime } from "../utils/formatTime";
import styles from "./UserProfilePage.module.css";

export default function UserProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const toast = useToast();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("listings");
  const [listings, setListings] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [followStatus, setFollowStatus] = useState(null);
  const [followBusy, setFollowBusy] = useState(false);

  useEffect(() => {
    setProfile(null);
    setListings(null);
    setReviews(null);
    setFollowStatus(null);
    getUserProfile(id).then(setProfile).catch(() => setError("Profil introuvable."));
    searchListings({ seller_id: id, page_size: 50 }).then((d) => setListings(d.items)).catch(() => setListings([]));
    getUserReviews(id).then(setReviews).catch(() => setReviews([]));
    if (currentUser && currentUser.id !== id) {
      getFollowStatus(id).then(setFollowStatus).catch(() => {});
    }
  }, [id, currentUser]);

  const isSelf = currentUser?.id === id;

  const toggleFollow = async () => {
    if (!currentUser) return navigate("/login");
    setFollowBusy(true);
    try {
      if (followStatus?.following) {
        await unfollowUser(id);
        setFollowStatus((s) => ({ ...s, following: false, followers_count: s.followers_count - 1 }));
      } else {
        await followUser(id);
        setFollowStatus((s) => ({ ...s, following: true, followers_count: (s?.followers_count || 0) + 1 }));
        toast.success(`Tu suis maintenant ${profile.display_name}`);
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur");
    } finally {
      setFollowBusy(false);
    }
  };

  if (error) return <div className={styles.errorPage}>{error}</div>;

  if (!profile) {
    return (
      <div className={styles.page}>
        <div className={styles.header}>
          <Skeleton variant="circle" width={72} height={72} />
          <Skeleton variant="text" width="40%" style={{ marginTop: 12 }} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <UserAvatar name={profile.display_name} src={profile.profile_photo_url} size="lg" />
        <p className={styles.name}>{profile.display_name}</p>
        <div className={styles.metaRow}>
          <RatingStars value={profile.average_rating} size={13} />
          <span>({profile.review_count})</span>
        </div>
        <div className={styles.trustRow}>
          {profile.city && (
            <span className={styles.trustItem}><MapPin size={13} strokeWidth={1.75} /> {profile.city}</span>
          )}
          <span className={styles.trustItem}>
            <Calendar size={13} strokeWidth={1.75} /> Membre depuis {new Date(profile.created_at).getFullYear()}
          </span>
          {followStatus && (
            <span className={styles.trustItem}>{followStatus.followers_count} abonné{followStatus.followers_count > 1 ? "s" : ""}</span>
          )}
        </div>
        {profile.bio && <p className={styles.bio}>{profile.bio}</p>}

        {!isSelf && (
          <div className={styles.actions}>
            <Button
              variant={followStatus?.following ? "secondary" : "primary"}
              onClick={toggleFollow}
              loading={followBusy}
            >
              {followStatus?.following ? "Ne plus suivre" : "Suivre"}
            </Button>
            <Button variant="secondary" onClick={() => navigate(`/messages`)}>
              <MessageSquare size={20} strokeWidth={1.75} /> Message
            </Button>
          </div>
        )}
      </div>

      <div className={styles.tabs}>
        <Chip active={tab === "listings"} onClick={() => setTab("listings")}>Annonces</Chip>
        <Chip active={tab === "reviews"} onClick={() => setTab("reviews")}>Avis</Chip>
      </div>

      {tab === "listings" && (
        listings === null ? (
          <div className={styles.grid}>
            {Array.from({ length: 4 }).map((_, i) => <ListingCardSkeleton key={i} />)}
          </div>
        ) : listings.length === 0 ? (
          <EmptyState icon={Tag} title="Aucune annonce" description="Cette personne n'a rien publié pour le moment." />
        ) : (
          <div className={styles.grid}>
            {listings.map((l) => <ListingCard key={l.id} listing={l} />)}
          </div>
        )
      )}

      {tab === "reviews" && (
        reviews === null ? (
          <Skeleton variant="text" width="60%" />
        ) : reviews.length === 0 ? (
          <EmptyState icon={MessageSquare} title="Aucun avis" description="Pas encore d'avis pour ce vendeur." />
        ) : (
          <div className={styles.reviewList}>
            {reviews.map((r) => (
              <div key={r.id} className={styles.reviewCard}>
                <div className={styles.reviewTop}>
                  <RatingStars value={r.rating} size={13} />
                  <span className={styles.reviewDate}>{formatRelativeTime(r.created_at)}</span>
                </div>
                {r.comment && <p className={styles.reviewComment}>{r.comment}</p>}
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
