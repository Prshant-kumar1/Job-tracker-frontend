import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/",
  preview: {
    allowedHosts: "all",
    host: "0.0.0.0",
    port: parseInt(process.env.PORT) || 10000,
  },
});
