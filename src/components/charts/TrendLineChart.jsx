import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

/**
 * Gradient-filled line chart for applications submitted per week.
 * labels: array of week labels, data: array of counts (same length).
 */
export default function TrendLineChart({ labels, data }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    const ctx = canvasRef.current.getContext("2d");
    const fill = ctx.createLinearGradient(0, 0, 0, 220);
    fill.addColorStop(0, "rgba(139,123,255,0.35)");
    fill.addColorStop(1, "rgba(139,123,255,0)");

    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            data,
            borderColor: "#8b7bff",
            backgroundColor: fill,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: "#8b7bff",
            pointBorderColor: "#0b0c1c",
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: "#7f7e98", font: { size: 11 } },
          },
          y: {
            beginAtZero: true,
            grid: { color: "rgba(255,255,255,0.06)" },
            ticks: { color: "#7f7e98", font: { size: 11 }, stepSize: 1, precision: 0 },
          },
        },
        animation: { duration: 900, easing: "easeOutQuart" },
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(labels), JSON.stringify(data)]);

  return (
    <div className="line-canvas-box">
      <canvas
        ref={canvasRef}
        role="img"
        aria-label="Line chart of applications submitted per week over the last 8 weeks"
      />
    </div>
  );
}
