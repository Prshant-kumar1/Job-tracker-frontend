import { useEffect, useRef, useState } from "react";

/**
 * Animates a number counting up from 0 to `value` whenever `value` changes.
 * Pure presentational — no side effects beyond the rAF loop, which is
 * always cleaned up on unmount/re-render.
 */
export default function AnimatedNumber({ value, duration = 900 }) {
  const [display, setDisplay] = useState(0);
  const frameRef = useRef(null);

  useEffect(() => {
    const target = Number(value) || 0;
    const start = performance.now();

    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplay(Math.round(eased * target));
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(step);
      }
    }

    frameRef.current = requestAnimationFrame(step);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [value, duration]);

  return <>{display}</>;
}
