import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

/**
 * Donut chart for status breakdown.
 * data: [{ label, value }], colors: array of hex strings in the same order.
 */
export default function DonutChart({ data, colors, total }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(canvasRef.current, {
      type: "doughnut",
      data: {
        labels: data.map((d) => d.label),
        datasets: [
          {
            data: data.map((d) => d.value),
            backgroundColor: colors,
            borderColor: "#0b0c1c",
            borderWidth: 3,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "72%",
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true },
        },
        animation: { animateRotate: true, duration: 800 },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(data), JSON.stringify(colors)]);

  return (
    <div className="donut-canvas-box">
      <canvas
        ref={canvasRef}
        role="img"
        aria-label={`Donut chart of application status breakdown, total ${total}`}
      />
      <div className="donut-center">
        <div className="n">{total}</div>
        <div className="l">total</div>
      </div>
    </div>
  );
}
