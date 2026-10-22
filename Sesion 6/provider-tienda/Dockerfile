# ============================================================
# Dockerfile — PROVIDER (API de la Tienda)
# Funciona igual con Docker o con Podman (mismo formato de imagen).
#   Docker:  docker build -t provider-tienda .
#   Podman:  podman build -t provider-tienda .
# ============================================================
FROM node:20-alpine

WORKDIR /app

# 1) Copiar package.json primero (mejor cache de capas).
#    Usamos --ignore-scripts para que el 'postinstall' NO corra todavia
#    (aun no existe datos/generar-datos.js en la imagen en este punto).
COPY package*.json ./
RUN npm install --omit=dev --ignore-scripts

# 2) Copiar el resto del codigo (ya incluye datos/generar-datos.js y el servidor)
COPY . .

# 3) Generar datos/db.json con Faker (ahora si existe el script)
RUN node datos/generar-datos.js

ENV PORT=3000
EXPOSE 3000

# Healthcheck: el orquestador marca el contenedor "healthy" si la API responde.
# OJO con Podman: construye con 'podman build --format docker ...' para que el
# HEALTHCHECK no se ignore (en formato OCI, el default de Podman, se descarta).
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "servidor/server.js"]
