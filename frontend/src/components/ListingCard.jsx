import { Link } from "react-router-dom";
import { COLORS, formatFCFA } from "../theme";

export default function ListingCard({ listing }) {
  return (
    <Link to={`/listings/${listing.id}`} style={{ textDecoration: "none", color: "inherit" }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <div
          style={{
            aspectRatio: "3/4",
            borderRadius: 16,
            overflow: "hidden",
            background: "#fff",
          }}
        >
          {listing.cover_image_url ? (
            <img
              src={listing.cover_image_url}
              alt={listing.title}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: COLORS.inkSoft,
                fontSize: 12,
              }}
            >
              Pas de photo
            </div>
          )}
        </div>
        <div style={{ paddingTop: 8 }}>
          <p style={{ fontSize: 15, fontWeight: 600, margin: 0, color: COLORS.ink }}>
            {formatFCFA(listing.price)}
          </p>
          <p
            style={{
              fontSize: 13,
              margin: "2px 0 0",
              color: COLORS.inkSoft,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {listing.title}
          </p>
          <p style={{ fontSize: 12, margin: "2px 0 0", color: COLORS.inkSoft }}>{listing.city}</p>
        </div>
      </div>
    </Link>
  );
}
