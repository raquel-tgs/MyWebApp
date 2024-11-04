/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*"],
  theme: {
    extend: {},
  },
  plugins: [],
}

// npx tailwindcss -i ./static/src/main.css -o ./static/css/main.css --watch