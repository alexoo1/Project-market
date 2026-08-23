import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, ImagePlus, X, Check } from "lucide-react";
import { getCategories, getBrands, createListing, updateListing, getListing, uploadImages } from "../api/endpoints";
import { formatFCFA, CONDITION_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/ToastProvider";
import { ApiError } from "../api/client";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import IconButton from "../components/ui/IconButton";
import Chip from "../components/ui/Chip";
import Skeleton from "../components/ui/Skeleton";
import styles from "./SellPage.module.css";

const STEPS = ["Photos", "Titre", "Catégorie", "Détails", "Description", "Prix & lieu", "Aperçu"];

const emptyForm = {
  title: "", description: "", category_id: "", brand_id: "", size: "", color: "",
  condition: "good", price: "", city: "", district: "",
};

export default function SellPage() {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(0);
  const [loadingListing, setLoadingListing] = useState(isEditMode);
  const fileInputRef = useRef(null);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
    getBrands().then(setBrands).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEditMode) return;
    getListing(id)
      .then((listing) => {
        if (user && listing.seller?.id !== user.id) {
          toast.error("Tu ne peux modifier que tes propres annonces.");
          navigate(`/listings/${id}`);
          return;
        }
        setForm({
          title: listing.title,
          description: listing.description,
          category_id: listing.category_id || "",
          brand_id: listing.brand_id || "",
          size: listing.size || "",
          color: listing.color || "",
          condition: listing.condition,
          price: String(listing.price),
          city: listing.city,
          district: listing.district || "",
        });
        setImages(listing.images.map((img) => img.url));
      })
      .catch(() => {
        toast.error("Annonce introuvable.");
        navigate("/profile");
      })
      .finally(() => setLoadingListing(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isEditMode, user]);

  if (!authLoading && !user) {
    navigate("/login");
    return null;
  }

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const removeImage = (idx) => setImages((imgs) => imgs.filter((_, i) => i !== idx));

  const handleFilesSelected = async (e) => {
    const files = Array.from(e.target.files || []).slice(0, 8 - images.length);
    e.target.value = "";
    if (files.length === 0) return;
    setUploading(true);
    try {
      const { images: uploaded } = await uploadImages(files);
      setImages((imgs) => [...imgs, ...uploaded.map((img) => img.url)]);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors de l'envoi des photos.");
    } finally {
      setUploading(false);
    }
  };

  const categoryName = categories.find((c) => c.id === form.category_id)?.name;
  const brandName = brands.find((b) => b.id === form.brand_id)?.name;

  const stepValid = [
    images.length > 0,
    form.title.trim().length >= 3,
    form.category_id !== "",
    true,
    form.description.trim().length >= 10,
    Number(form.price) > 0 && form.city.trim() !== "",
    true,
  ][step];

  const goNext = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const goBack = () => (step === 0 ? navigate(-1) : setStep((s) => s - 1));

  const handlePublish = async () => {
    setBusy(true);
    try {
      const payload = {
        ...form,
        price: Number(form.price),
        brand_id: form.brand_id || undefined,
        district: form.district || undefined,
        images: images.map((url) => ({ url })),
      };
      if (isEditMode) {
        await updateListing(id, payload);
        toast.success("Annonce mise à jour !");
        navigate(`/listings/${id}`);
      } else {
        const listing = await createListing(payload);
        toast.success("Annonce publiée !");
        navigate(`/listings/${listing.id}`);
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Erreur lors de la publication.");
    } finally {
      setBusy(false);
    }
  };

  if (loadingListing) {
    return (
      <div className={styles.page}>
        <div className={styles.content}>
          <div className={styles.step}>
            <Skeleton variant="text" width="50%" height={28} />
            <Skeleton height={160} style={{ marginTop: 16 }} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <IconButton icon={ArrowLeft} label="Précédent" onClick={goBack} />
        <div className={styles.progress}>
          <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
          </div>
          <p className={styles.progressLabel}>{STEPS[step]} · {step + 1}/{STEPS.length}</p>
        </div>
      </div>

      <div className={styles.content}>
        {step === 0 && (
          <StepPhotos
            images={images}
            uploading={uploading}
            fileInputRef={fileInputRef}
            onSelect={handleFilesSelected}
            onRemove={removeImage}
          />
        )}

        {step === 1 && (
          <StepShell title="Comment veux-tu appeler ton article ?">
            <Input placeholder="Ex. Veste en jean oversize" value={form.title} onChange={set("title")} autoFocus />
          </StepShell>
        )}

        {step === 2 && (
          <StepShell title="Dans quelle catégorie ?">
            <div className={styles.chipGrid}>
              {categories.map((c) => (
                <Chip key={c.id} active={form.category_id === c.id} onClick={() => setForm((f) => ({ ...f, category_id: c.id }))}>
                  {c.name}
                </Chip>
              ))}
            </div>
            <p className={styles.subLabel}>Marque (facultatif)</p>
            <div className={styles.chipGrid}>
              {brands.map((b) => (
                <Chip
                  key={b.id}
                  active={form.brand_id === b.id}
                  onClick={() => setForm((f) => ({ ...f, brand_id: f.brand_id === b.id ? "" : b.id }))}
                >
                  {b.name}
                </Chip>
              ))}
            </div>
          </StepShell>
        )}

        {step === 3 && (
          <StepShell title="Quelques détails">
            <div className={styles.row}>
              <Input placeholder="Taille (facultatif)" value={form.size} onChange={set("size")} />
              <Input placeholder="Couleur (facultatif)" value={form.color} onChange={set("color")} />
            </div>
            <p className={styles.subLabel}>État</p>
            <div className={styles.chipGrid}>
              {Object.entries(CONDITION_LABELS).map(([val, label]) => (
                <Chip key={val} active={form.condition === val} onClick={() => setForm((f) => ({ ...f, condition: val }))}>
                  {label}
                </Chip>
              ))}
            </div>
          </StepShell>
        )}

        {step === 4 && (
          <StepShell title="Décris ton article">
            <textarea
              placeholder="Matière, coupe, défauts éventuels, raison de la vente..."
              aria-label="Description de l'article"
              value={form.description}
              onChange={set("description")}
              rows={7}
              className={styles.textarea}
              autoFocus
            />
          </StepShell>
        )}

        {step === 5 && (
          <StepShell title="Prix et localisation">
            <Input placeholder="Prix en FCFA" type="number" value={form.price} onChange={set("price")} />
            <div className={styles.row}>
              <Input placeholder="Ville" value={form.city} onChange={set("city")} />
              <Input placeholder="Quartier (facultatif)" value={form.district} onChange={set("district")} />
            </div>
          </StepShell>
        )}

        {step === 6 && (
          <StepPreview
            images={images}
            form={form}
            categoryName={categoryName}
            brandName={brandName}
          />
        )}
      </div>

      <div className={styles.footer}>
        {step < STEPS.length - 1 ? (
          <Button fullWidth size="lg" disabled={!stepValid || uploading} onClick={goNext}>
            Continuer <ArrowRight size={16} strokeWidth={2.5} />
          </Button>
        ) : (
          <Button fullWidth size="lg" loading={busy} onClick={handlePublish}>
            <Check size={16} strokeWidth={2.5} /> {isEditMode ? "Enregistrer les modifications" : "Publier l'annonce"}
          </Button>
        )}
      </div>
    </div>
  );
}

function StepShell({ title, children }) {
  return (
    <div className={styles.step}>
      <h2 className={styles.stepTitle}>{title}</h2>
      {children}
    </div>
  );
}

function StepPhotos({ images, uploading, fileInputRef, onSelect, onRemove }) {
  return (
    <StepShell title="Ajoute des photos">
      <input ref={fileInputRef} type="file" accept="image/*" multiple onChange={onSelect} className={styles.hiddenInput} />
      <div className={styles.photoGrid}>
        {images.map((url, idx) => (
          <div key={idx} className={styles.photoTile}>
            <img src={url} alt="" />
            <button type="button" onClick={() => onRemove(idx)} className={styles.photoRemove} aria-label="Retirer la photo">
              <X size={12} strokeWidth={2.5} />
            </button>
          </div>
        ))}
        {images.length < 8 && (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className={styles.photoAdd}
          >
            <ImagePlus size={22} strokeWidth={1.75} />
            <span>{uploading ? "Envoi..." : "Ajouter"}</span>
          </button>
        )}
      </div>
      <p className={styles.hint}>{images.length}/8 photos — la première sera la couverture de l'annonce.</p>
    </StepShell>
  );
}

function StepPreview({ images, form, categoryName, brandName }) {
  return (
    <StepShell title="Vérifie ton annonce">
      <div className={styles.previewCard}>
        {images[0] && <img src={images[0]} alt="" className={styles.previewImage} />}
        <div className={styles.previewBody}>
          <p className={styles.previewPrice}>{form.price ? formatFCFA(Number(form.price)) : "—"}</p>
          <p className={styles.previewTitle}>{form.title}</p>
          <p className={styles.previewMeta}>
            {[categoryName, brandName, CONDITION_LABELS[form.condition]].filter(Boolean).join(" · ")}
          </p>
          <p className={styles.previewMeta}>{[form.city, form.district].filter(Boolean).join(", ")}</p>
          <p className={styles.previewDescription}>{form.description}</p>
        </div>
      </div>
    </StepShell>
  );
}
