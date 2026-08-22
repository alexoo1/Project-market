import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { COLORS } from "../theme";
import { ApiError } from "../api/client";
import { inputStyle, buttonStyle } from "./LoginPage";

export default function RegisterPage() {
  const [form, setForm] = useState({
    first_name: "", display_name: "", phone: "", email: "", password: "", city: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const payload = { ...form };
      if (!payload.email) delete payload.email;
      await register(payload);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur d'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "40px 20px", maxWidth: 400, margin: "0 auto" }}>
      <h1 style={{ color: COLORS.lagoon, fontSize: 24, fontWeight: 700 }}>Créer un compte</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 20 }}>
        <input placeholder="Prénom" value={form.first_name} onChange={set("first_name")} required style={inputStyle} />
        <input placeholder="Pseudo" value={form.display_name} onChange={set("display_name")} required style={inputStyle} />
        <input placeholder="Téléphone (+225...)" value={form.phone} onChange={set("phone")} required style={inputStyle} />
        <input placeholder="Email (facultatif)" value={form.email} onChange={set("email")} style={inputStyle} />
        <input placeholder="Ville" value={form.city} onChange={set("city")} style={inputStyle} />
        <input
          placeholder="Mot de passe (8 caractères min.)"
          type="password"
          value={form.password}
          onChange={set("password")}
          required
          minLength={8}
          style={inputStyle}
        />
        {error && <p style={{ color: COLORS.danger, fontSize: 13 }}>{error}</p>}
        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? "Création..." : "Créer mon compte"}
        </button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13, color: COLORS.inkSoft }}>
        Déjà un compte ? <Link to="/login" style={{ color: COLORS.coral }}>Se connecter</Link>
      </p>
    </div>
  );
}
