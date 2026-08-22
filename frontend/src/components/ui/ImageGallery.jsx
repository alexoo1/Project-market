import { useRef, useState } from "react";
import { ImageOff } from "lucide-react";
import styles from "./ImageGallery.module.css";

export default function ImageGallery({ images = [], alt = "" }) {
  const [active, setActive] = useState(0);
  const trackRef = useRef(null);

  const handleScroll = () => {
    const track = trackRef.current;
    if (!track) return;
    const index = Math.round(track.scrollLeft / track.clientWidth);
    setActive(index);
  };

  const goTo = (index) => {
    const track = trackRef.current;
    if (!track) return;
    track.scrollTo({ left: index * track.clientWidth, behavior: "smooth" });
  };

  if (images.length === 0) {
    return (
      <div className={styles.placeholder}>
        <ImageOff size={28} strokeWidth={1.75} aria-hidden="true" />
      </div>
    );
  }

  return (
    <div className={styles.gallery}>
      <div className={styles.track} ref={trackRef} onScroll={handleScroll}>
        {images.map((img, i) => (
          <div className={styles.slide} key={img.id || i}>
            <img src={img.url} alt={i === 0 ? alt : ""} className={styles.image} loading={i === 0 ? "eager" : "lazy"} />
          </div>
        ))}
      </div>
      {images.length > 1 && (
        <div className={styles.dots} role="tablist" aria-label="Photos de l'annonce">
          {images.map((_, i) => (
            <button
              key={i}
              type="button"
              role="tab"
              aria-selected={i === active}
              aria-label={`Photo ${i + 1} sur ${images.length}`}
              className={[styles.dot, i === active ? styles.dotActive : ""].filter(Boolean).join(" ")}
              onClick={() => goTo(i)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
