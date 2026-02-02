/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["\"Shippori Mincho\"", "serif"],
        sans: ["\"Zen Kaku Gothic New\"", "sans-serif"],
      },
      colors: {
        ink: "#1f2a33",
        muted: "#4b5a66",
        accent: "#0f766e",
        accent2: "#f59e0b",
      },
      boxShadow: {
        soft: "0 18px 40px rgba(17, 24, 39, 0.08)",
      },
    },
  },
  plugins: [],
};
