import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The dev server proxies /api to a cloa-viewer running on its default port, so
// `npm run dev` shows live view files without a rebuild of the page.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "dist" },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8765",
    },
  },
});
