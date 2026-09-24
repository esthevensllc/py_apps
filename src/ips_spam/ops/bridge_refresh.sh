#!/usr/bin/env bash
set -Eeuo pipefail

BASE_DIR="${UCEPROTECT_BRIDGE_BASE_DIR:-/opt/uceprotect_manual}"
RSYNC_BASE="${UCEPROTECT_RSYNC_BASE:-rsync-mirrors.uceprotect.net::RBLDNS-ALL}"
ASN_URL="${UCEPROTECT_ASN_URL:-https://www.uceprotect.net/de/l3charts.php}"
RSYNC_BINARY="${UCEPROTECT_RSYNC_BINARY:-rsync}"
CURL_BINARY="${UCEPROTECT_CURL_BINARY:-curl}"
TIMEOUT="${UCEPROTECT_RSYNC_TIMEOUT_SECONDS:-180}"
STAMP="$(date +%Y%m%d_%H%M%S)_$$"
SNAPSHOT_DIR="$BASE_DIR/snapshots/$STAMP"
RAW_DIR="$SNAPSHOT_DIR/raw"
STORAGE_DIR="$SNAPSHOT_DIR/storage"
PUBLISHED=0

mkdir -p "$RAW_DIR" \
  "$STORAGE_DIR/rsync/lvl1" \
  "$STORAGE_DIR/rsync/lvl2" \
  "$STORAGE_DIR/rsync/lvl3" \
  "$STORAGE_DIR/rsync/backscatter" \
  "$STORAGE_DIR/rsync/whitelist" \
  "$STORAGE_DIR/html" \
  "$BASE_DIR/logs"
chgrp uceprotect-readers "$SNAPSHOT_DIR" "$STORAGE_DIR"
chmod g+s "$SNAPSHOT_DIR" "$STORAGE_DIR"

cleanup() {
  if [[ "$PUBLISHED" -eq 0 && -n "${SNAPSHOT_DIR:-}" && -d "$SNAPSHOT_DIR" ]]; then
    rm -rf -- "$SNAPSHOT_DIR"
  fi
}
trap cleanup ERR

echo "UCEPROTECT_BRIDGE_START timestamp=$STAMP"

# Una sola sesión con el mirror para respetar su límite de frecuencia.
"$RSYNC_BINARY" -avz \
  --partial \
  --delay-updates \
  "--timeout=$TIMEOUT" \
  "$RSYNC_BASE/" \
  "$RAW_DIR/"

copy_source() {
  local source_name="$1"
  local target_name="$2"
  local source_path="$RAW_DIR/$source_name"
  if [[ ! -e "$source_path" ]]; then
    echo "Falta fuente rsync requerida: $source_name" >&2
    return 1
  fi
  cp -a -- "$source_path" "$STORAGE_DIR/rsync/$target_name/"
}

copy_source 'dnsbl-1.uceprotect.net' 'lvl1'
copy_source 'dnsbl-2.uceprotect.net' 'lvl2'
copy_source 'dnsbl-3.uceprotect.net' 'lvl3'
copy_source 'ips.backscatterer.org' 'backscatter'
copy_source 'ips.whitelisted.org' 'whitelist'

"$CURL_BINARY" -fL \
  --retry 3 \
  --connect-timeout 20 \
  --max-time 120 \
  -A 'py_apps-ips-spam/1.0' \
  -o "$STORAGE_DIR/html/l3charts.html.tmp" \
  "$ASN_URL"
test -s "$STORAGE_DIR/html/l3charts.html.tmp"
grep -Eqi 'UCEPROTECT|Spam-Score|Provider' "$STORAGE_DIR/html/l3charts.html.tmp"
mv -- "$STORAGE_DIR/html/l3charts.html.tmp" "$STORAGE_DIR/html/l3charts.html"

# La cuenta técnica del puente necesita lectura y recorrido, no escritura.
chgrp -R uceprotect-readers "$SNAPSHOT_DIR"
chmod -R g+rX,o-rwx "$SNAPSHOT_DIR"
find "$SNAPSHOT_DIR" -type d -exec chmod g+s {} +
date +%s > "$STORAGE_DIR/READY"

# Publicar cambiando un symlink: una descarga incompleta nunca reemplaza la vigente.
ln -s -- "$STORAGE_DIR" "$BASE_DIR/.current-$STAMP"
PUBLISHED=1
mv -Tf -- "$BASE_DIR/.current-$STAMP" "$BASE_DIR/current"
trap - ERR

# Conservar la instantánea recién publicada y las dos anteriores.
find "$BASE_DIR/snapshots" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
  | sort -nr \
  | awk 'NR > 3 { $1=""; sub(/^ /, ""); print }' \
  | while IFS= read -r old_snapshot; do
      [[ -n "$old_snapshot" ]] && rm -rf -- "$old_snapshot"
    done

echo "UCEPROTECT_BRIDGE_OK current=$BASE_DIR/current"
