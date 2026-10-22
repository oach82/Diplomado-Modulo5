# ============================================================
# Dockerfile — CONSUMER (servicio de notificaciones) + su test Pact
# Corre el test del consumer DENTRO de un contenedor Linux. Asi evitamos el
# limite de rutas largas de Windows (pact-python trae un Ruby embebido) y es
# coherente con el dia: todo en contenedores.
#   Docker:  docker build -t consumer-notificaciones .
#   Podman:  podman build -t consumer-notificaciones .
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Por defecto, correr el test del consumer: genera el contrato (pact file).
# El contrato se escribe en /pacts (se monta como volumen para compartirlo
# con la verificacion del provider).
CMD ["pytest", "-v"]
