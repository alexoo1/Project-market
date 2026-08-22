import { NavLink } from "react-router-dom";
import { COLORS } from "../theme";

const items = [
  { to: "/", label: "Accueil", icon: "🏠" },
  { to: "/search", label: "Recherche", icon: "🔍" },
  { to: "/sell", label: "Vendre", icon: "➕", isCenter: true },
  { to: "/messages", label: "Messages", icon: "💬" },
  { to: "/profile", label: "Profil", icon: "👤" },
];

export default function BottomNav() {
  return (
    <nav
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: 64,
        background: "#fff",
        borderTop: `1px solid ${COLORS.sandDeep}`,
        display: "flex",
        alignItems: "center",
        zIndex: 50,
      }}
    >
      {items.map((item) =>
        item.isCenter ? (
          <div key={item.to} style={{ flex: 1, display: "flex", justifyContent: "center" }}>
            <NavLink
              to={item.to}
              style={{
                width: 48,
                height: 48,
                borderRadius: "50%",
                background: COLORS.coral,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: -24,
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                fontSize: 20,
                color: "#fff",
                textDecoration: "none",
              }}
            >
              {item.icon}
            </NavLink>
          </div>
        ) : (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              textDecoration: "none",
              color: isActive ? COLORS.lagoon : "#B7B0A2",
              fontSize: 10,
              fontWeight: 500,
            })}
          >
            <span style={{ fontSize: 18 }}>{item.icon}</span>
            {item.label}
          </NavLink>
        )
      )}
    </nav>
  );
}
