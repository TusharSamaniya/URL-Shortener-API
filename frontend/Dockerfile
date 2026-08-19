# Serve the static frontend with nginx (tiny, fast, production-ready).
FROM nginx:alpine

# Copy the 3 frontend files into nginx's default serve directory.
COPY index.html styles.css app.js /usr/share/nginx/html/

# Expose port 80 (nginx default). docker-compose will map this to 5500 on host.
EXPOSE 80

# nginx runs in foreground by default — no CMD needed.