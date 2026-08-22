import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { COLORS } from "../theme";
import { ApiError } from "../api/client";

export default function LoginPage() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(identifier, password);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Erreur de connexion");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "40px 20px", maxWidth: 400, margin: "0 auto" }}>
      <h1 style={{ color: COLORS.lagoon, fontSize: 24, fontWeight: 700 }}>Connexion</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 20 }}>
        <input
          placeholder="Téléphone ou email"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          placeholder="Mot de passe"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />
        {error && <p style={{ color: COLORS.danger, fontSize: 13 }}>{error}</p>}
        <button type="submit" disabled={loading} style={buttonStyle}>
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
      <p style={{ marginTop: 16, fontSize: 13, color: COLORS.inkSoft }}>
        Pas encore de compte ? <Link to="/register" style={{ color: COLORS.coral }}>Créer un compte</Link>
      </p>
    </div>
  );
}

export const inputStyle = {
  padding: "12px 16px",
  borderRadius: 24,
  border: `1px solid ${COLORS.sandDeep}`,
  fontSize: 14,
  outline: "none",
};

export const buttonStyle = {
  padding: "12px 16px",
  borderRadius: 24,
  border: "none",
  background: COLORS.lagoon,
  color: COLORS.sand,
  fontSize: 14,
  fontWeight: 600,
  cursor: "pointer",
};
