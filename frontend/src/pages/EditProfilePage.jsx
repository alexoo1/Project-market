import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Camera, ArrowLeft } from "lucide-react";
import { updateProfile, changePassword, uploadImages } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import UserAvatar from "../components/ui/UserAvatar";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import IconButton from "../components/ui/IconButton";
import styles from "./EditProfilePage.module.css";

export default function EditProfilePage() {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const fileInputRef = useRef(null);

  const [form, setForm] = useState({
    display_name: user?.display_name || "",
    bio: user?.bio || "",
    city: user?.city || "",
    district: user?.district || "",
  });
  const [photoUrl, setPhotoUrl] = useState(user?.profile_photo_url || null);
  const [uploading, setUploading] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);

  if (!user) return null;

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handlePhotoChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setUploading(true);
    try {
      const { images } = await uploadImages([file]);
      setPhotoUrl(images[0].url);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors de l'envoi de la photo.");
    } finally {
      setUploading(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      await updateProfile({ ...form, profile_photo_url: photoUrl });
      await refreshUser();
      toast.success("Profil mis à jour.");
      navigate("/profile");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors de la mise à jour.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setSavingPassword(true);
    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword });
      toast.success("Mot de passe changé.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors du changement de mot de passe.");
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <IconButton icon={ArrowLeft} label="Retour" onClick={() => navigate(-1)} />
        <p className={styles.headerTitle}>Modifier le profil</p>
      </div>

      <form onSubmit={handleSaveProfile} className={styles.section}>
        <div className={styles.photoRow}>
          <div className={styles.photoWrap}>
            <UserAvatar name={form.display_name} src={photoUrl} size="lg" />
            <button
              type="button"
              className={styles.photoButton}
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              aria-label="Changer la photo de profil"
            >
              <Camera size={15} strokeWidth={2} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className={styles.hiddenInput}
              onChange={handlePhotoChange}
            />
          </div>
          {uploading && <p className={styles.hint}>Envoi de la photo...</p>}
        </div>

        <Input label="Pseudo" value={form.display_name} onChange={set("display_name")} required />
        <div className={styles.field}>
          <label className={styles.label}>Bio</label>
          <textarea
            value={form.bio}
            onChange={set("bio")}
            rows={3}
            className={styles.textarea}
            placeholder="Parle un peu de toi..."
          />
        </div>
        <div className={styles.row}>
          <Input label="Ville" value={form.city} onChange={set("city")} />
          <Input label="Quartier" value={form.district} onChange={set("district")} />
        </div>
        <Button type="submit" loading={savingProfile} fullWidth size="lg">
          Enregistrer
        </Button>
      </form>

      <form onSubmit={handleChangePassword} className={styles.section}>
        <p className={styles.sectionTitle}>Changer le mot de passe</p>
        <Input
          label="Mot de passe actuel"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
        />
        <Input
          label="Nouveau mot de passe"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          minLength={8}
          required
        />
        <Button type="submit" variant="secondary" loading={savingPassword} fullWidth>
          Changer le mot de passe
        </Button>
      </form>
    </div>
  );
}
