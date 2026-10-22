# ============================================================
# DIA 7 - Calculadora DORA en un contenedor (Podman)
# ============================================================
# Empaqueta el script Node que calcula las 4 metricas DORA a partir de
# deployments.json. Sin dependencias: solo Node.
# ============================================================
FROM node:20-alpine

WORKDIR /app

COPY calcular-dora.js /app/calcular-dora.js
COPY deployments.json /app/deployments.json

# Por defecto lee el deployments.json copiado en la imagen.
# Para usar tus propios datos, monta un volumen y apunta DEPLOYMENTS_FILE.
CMD ["node", "calcular-dora.js"]
