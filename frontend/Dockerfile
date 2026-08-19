# Serve the static frontend with nginx (tiny, fast, production-ready).
FROM nginx:alpine

# Build-time arg so CI/docker-compose can inject the real API URL.
# Falls back to localhost for local development.
ARG API_BASE_URL=http://localhost:8000

# Copy the 3 frontend files into nginx's default serve directory.
COPY index.html styles.css /usr/share/nginx/html/

# Inject the API_BASE_URL into app.js at build time so the
# frontend knows where the backend lives without hardcoding it.
COPY app.js /tmp/app.js
RUN sed "s|http://localhost:8000|${API_BASE_URL}|g" /tmp/app.js \
    > /usr/share/nginx/html/app.js

# Expose port 80 (nginx default). docker-compose will map this to 5500 on host.
EXPOSE 80

# nginx runs in foreground by default — no CMD needed.
