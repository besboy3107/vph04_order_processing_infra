#!/usr/bin/env bash
set -Eeuo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Если аргументы не переданы — берём учётку из .env (REGISTRY_USER/REGISTRY_PASSWORD).
if [[ $# -eq 0 && -f "${script_dir}/../.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source "${script_dir}/../.env"; set +a
  username="${REGISTRY_USER:-}"
  password="${REGISTRY_PASSWORD:-}"
elif [[ $# -eq 2 ]]; then
  username="$1"
  password="$2"
else
  echo "Usage: $0 <username> <password>   (или заполните REGISTRY_USER/REGISTRY_PASSWORD в .env и запустите без аргументов)" >&2
  exit 64
fi

if [[ -z "${username}" || -z "${password}" ]]; then
  echo "Не задан пользователь или пароль реестра." >&2
  exit 64
fi

auth_dir="${script_dir}/auth"
mkdir -p "$auth_dir"
docker run --rm httpd:2-alpine htpasswd -Bbn "$username" "$password" > "$auth_dir/htpasswd"
chmod 600 "$auth_dir/htpasswd"
echo "Registry user '$username' created in $auth_dir/htpasswd"
