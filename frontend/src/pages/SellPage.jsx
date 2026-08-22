import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCategories, getBrands, createListing } from "../api/endpoints";
import { COLORS, CONDITION_LABELS } from "../theme";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import { inputStyle, buttonStyle } from "./LoginPage";

export default function SellPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [imageUrl, setImageUrl] = useState("");
  const [images, setImages] = useState([]);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    title: "", description: "", category_id: "", brand_id: "", size: "", color: "",
    condition: "good", price: "", city: "", district: "",
  });

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
    getBrands().then(setBrands).catch(() => {});
  }, []);

  if (!authLoading && !user) {
    navigate("/login");
    return null;
  }

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const addImage = () => {
    if (!imageUrl.trim()) return;
    if (images.length >= 8) return;
    setImages((imgs) => [...imgs, imageUrl.trim()]);
    setImageUrl("");
  };

  const removeImage = (idx) => setImages((imgs) => imgs.filter((_, i) => i !== idx));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (images.length === 0) {
      setError("Ajoute au moins une photo (une URL d'image).");
      return;
    }
    setBusy(true);
    try {
      const payload = {
        ...form,
        price: Number(form.price),
        brand_id: form.brand_id || undefined,
        district: form.district || undefined,
        images: images.map((url) => ({ url })),
      };
      const listing = await createListing(payload);
      navigate(`/listings/${listing.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur lors de la publication.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: "20px 16px 100px", maxWidth: 480, margin: "0 auto" }}>
      <h1 style={{ fontSize: 20, fontWeight: 700, color: COLORS.lagoon }}>Publier un article</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 16 }}>
        <div>
          <label style={labelStyle}>Photos ({images.length}/8)</label>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              placeholder="URL d'une photo"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              style={{ ...inputStyle, flex: 1 }}
            />
            <button type="button" onClick={addImage} style={{ ...buttonStyle, background: COLORS.coral }}>
              Ajouter
            </button>
          </div>
          {images.length > 0 && (
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
              {images.map((url, idx) => (
                <div key={idx} style={{ position: "relative", width: 56, height: 56 }}>
                  <img src={url} alt="" style={{ width: 56, height: 56, objectFit: "cover", borderRadius: 8 }} />
                  <button
                    type="button"
                    onClick={() => removeImage(idx)}
                    style={{
                      position: "absolute", top: -6, right: -6, width: 18, height: 18, borderRadius: "50%",
                      background: COLORS.danger, color: "#fff", border: "none", fontSize: 10, cursor: "pointer",
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <input placeholder="Titre" value={form.title} onChange={set("title")} required style={inputStyle} />
        <textarea
          placeholder="Description"
          value={form.description}
          onChange={set("description")}
          required
          rows={4}
          style={{ ...inputStyle, borderRadius: 16, resize: "vertical" }}
        />

        <select value={form.category_id} onChange={set("category_id")} required style={inputStyle}>
          <option value="">Catégorie</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <select value={form.brand_id} onChange={set("brand_id")} style={inputStyle}>
          <option value="">Marque (facultatif)</option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>

        <div style={{ display: "flex", gap: 8 }}>
          <input placeholder="Taille" value={form.size} onChange={set("size")} style={{ ...inputStyle, flex: 1 }} />
          <input placeholder="Couleur" value={form.color} onChange={set("color")} style={{ ...inputStyle, flex: 1 }} />
        </div>

        <select value={form.condition} onChange={set("condition")} required style={inputStyle}>
          {Object.entries(CONDITION_LABELS).map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>

        <input
          placeholder="Prix en FCFA"
          type="number"
          value={form.price}
          onChange={set("price")}
          required
          style={inputStyle}
        />

        <div style={{ display: "flex", gap: 8 }}>
          <input placeholder="Ville" value={form.city} onChange={set("city")} required style={{ ...inputStyle, flex: 1 }} />
          <input placeholder="Quartier" value={form.district} onChange={set("district")} style={{ ...inputStyle, flex: 1 }} />
        </div>

        {error && <p style={{ color: COLORS.danger, fontSize: 13 }}>{error}</p>}

        <button type="submit" disabled={busy} style={buttonStyle}>
          {busy ? "Publication..." : "Publier l'article"}
        </button>
      </form>
    </div>
  );
}

const labelStyle = { fontSize: 12, color: COLORS.inkSoft, marginBottom: 4, display: "block" };
