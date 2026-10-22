# ============================================================
# Dockerfile — VERIFICACION DEL PROVIDER (lado provider de Pact)
# Corre dentro de un contenedor Linux (evita el limite de rutas de Windows).
#   Docker:  docker build -t provider-verify .
#   Podman:  podman build -t provider-verify .
# ============================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verifica el provider contra el contrato. El provider debe estar corriendo y
# accesible por red (PROVIDER_URL). El contrato se monta en /pacts.
CMD ["python", "verificar_provider.py"]
