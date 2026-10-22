# ============================================================
# Dockerfile — APP TIENDA (front + API). SUT del Dia 5/6.
# Funciona igual con Podman o Docker (imagen OCI).
#   podman build -t app-tienda ./app-tienda
#   podman run -d --name app-tienda -p 3000:3000 app-tienda
# ============================================================
FROM node:20-alpine

WORKDIR /app

# 1) package.json primero (mejor cache de capas).
#    --ignore-scripts evita que el postinstall corra antes de copiar el codigo.
COPY package*.json ./
RUN npm install --omit=dev --ignore-scripts

# 2) Copiar el resto (servidor, datos, public)
COPY . .

# 3) Generar datos/db.json con Faker (semilla fija → datos deterministas)
RUN node datos/generar-datos.js

ENV PORT=3000
EXPOSE 3000

# OJO con Podman: construye con 'podman build --format docker ...' para que el
# HEALTHCHECK no se ignore (en formato OCI, el default de Podman, se descarta).
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "servidor/server.js"]
