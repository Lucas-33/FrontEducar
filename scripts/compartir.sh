#!/usr/bin/env bash
# Comparte la app local mediante un túnel rápido de Cloudflare.
#
# Uso (desde la raíz del proyecto):
#   ./scripts/compartir.sh
#
# Requiere: uv y PostgreSQL iniciado (pg_ctl -D .pgdata start).
# Si cloudflared no está instalado, lo descarga en ~/.local/bin.

set -euo pipefail

cd "$(dirname "$0")/.."

CLOUDFLARED="${CLOUDFLARED:-$HOME/.local/bin/cloudflared}"
LOG_DIR="${TMPDIR:-/tmp}/opencode"
APP_LOG="$LOG_DIR/educar-app.log"
TUNNEL_LOG="$LOG_DIR/cloudflared.log"

mkdir -p "$LOG_DIR"

if ! command -v "$CLOUDFLARED" >/dev/null 2>&1; then
  echo "cloudflared no encontrado; instalando en ~/.local/bin..."
  mkdir -p "$(dirname "$CLOUDFLARED")"
  curl -fsSL -o "$CLOUDFLARED" \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod +x "$CLOUDFLARED"
fi

if ! curl -sf -o /dev/null http://127.0.0.1:8000/; then
  echo "Iniciando API + interfaz Flet en http://127.0.0.1:8000 ..."
  nohup uv run python frontend/run.py >"$APP_LOG" 2>&1 &
  for _ in $(seq 1 30); do
    sleep 2
    curl -sf -o /dev/null http://127.0.0.1:8000/ && break
  done
fi

echo "Iniciando túnel de Cloudflare..."
nohup "$CLOUDFLARED" tunnel --url http://localhost:8000 --no-autoupdate \
  >"$TUNNEL_LOG" 2>&1 &

for _ in $(seq 1 40); do
  sleep 2
  URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -1 || true)
  if [ -n "$URL" ]; then
    echo
    echo "App compartida en: $URL"
    echo "Swagger:           $URL/docs"
    echo
    echo "Logs: $APP_LOG | $TUNNEL_LOG"
    exit 0
  fi
done

echo "No se pudo obtener la URL del túnel. Revisá $TUNNEL_LOG" >&2
exit 1
