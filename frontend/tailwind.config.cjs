/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        tgBg: "#0e1621",
        tgSurface: "#17212b",
        tgAccent: "#5eb5f7"
      }
    }
  },
  plugins: []
};

