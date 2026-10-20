#!/usr/bin/env bash
# Instala o bot como serviço systemd do usuário, iniciando junto com o computador.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
conf="$HOME/.config/ibm-bot/env"

mkdir -p "$(dirname "$conf")" "$HOME/.config/systemd/user"
if [ ! -f "$conf" ]; then
  printf 'TELEGRAM_TOKEN=\nTELEGRAM_ALLOWED_IDS=\n' > "$conf"
  chmod 600 "$conf"
  echo "Criei $conf — preencha o token e o seu id e rode este script de novo."
  exit 0
fi

cp "$here/ibm-bot.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now ibm-bot.service
# Sem linger o serviço só sobe depois do login; com ele, sobe no boot.
loginctl enable-linger "$USER"
systemctl --user restart ibm-bot.service
systemctl --user --no-pager status ibm-bot.service | head -5
