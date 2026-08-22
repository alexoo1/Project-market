import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { User, AtSign, Phone, MapPin, Lock } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import styles from "./AuthPage.module.css";

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
    <div className={styles.page}>
      <div className={styles.card}>
        <p className={styles.eyebrow}>Bienvenue</p>
        <h1 className={styles.title}>Créer un compte</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input icon={User} placeholder="Prénom" value={form.first_name} onChange={set("first_name")} required />
          <Input icon={User} placeholder="Pseudo" value={form.display_name} onChange={set("display_name")} required />
          <Input icon={Phone} placeholder="Téléphone (+225...)" value={form.phone} onChange={set("phone")} required />
          <Input icon={AtSign} placeholder="Email (facultatif)" value={form.email} onChange={set("email")} />
          <Input icon={MapPin} placeholder="Ville" value={form.city} onChange={set("city")} />
          <Input
            icon={Lock}
            placeholder="Mot de passe (8 caractères min.)"
            type="password"
            value={form.password}
            onChange={set("password")}
            required
            minLength={8}
          />
          {error && <p className={styles.error}>{error}</p>}
          <Button type="submit" loading={loading} fullWidth size="lg">
            Créer mon compte
          </Button>
        </form>
        <p className={styles.footer}>
          Déjà un compte ? <Link to="/login" className={styles.link}>Se connecter</Link>
        </p>
      </div>
    </div>
  );
}
