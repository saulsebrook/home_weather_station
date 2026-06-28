#!/usr/bin/env bash
#
# restore.sh — deploy the captured configs onto a fresh Pi and re-enable services.
# Prompts you for each secret (nothing sensitive is stored in the repo).
#
# Run on the NEW Pi, from the infrastructure/ dir, after cloning the repo and
# installing the packages (see README.md).
#
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

confirm() { read -rp "$1 [y/N] " a; [[ "$a" =~ ^[Yy]$ ]]; }

echo "This copies configs from the repo onto THIS Pi and overwrites system files."
confirm "Continue?" || { echo "Aborted."; exit 1; }

echo "== service configs =="
sudo cp "$HERE/configs/dnsmasq/dnsmasq.conf"     /etc/dnsmasq.conf
[[ -d "$HERE/configs/dnsmasq/dnsmasq.d" ]] && sudo cp -r "$HERE/configs/dnsmasq/dnsmasq.d/." /etc/dnsmasq.d/
sudo cp "$HERE/configs/readsb/default-readsb"    /etc/default/readsb
sudo cp "$HERE/configs/lighttpd/lighttpd.conf"   /etc/lighttpd/lighttpd.conf
# rtl_airband: adjust target path to match your install if needed
sudo cp "$HERE/configs/airband/rtl_airband.conf" /etc/rtl_airband.conf
echo "  configs copied."

echo "== systemd units =="
sudo cp "$HERE/systemd/"*.service "$HERE/systemd/"*.timer /etc/systemd/system/ 2>/dev/null || true
sudo systemctl daemon-reload
echo "  units copied."

echo
echo "== SECRETS — paste these in by hand =="
echo "Opening each secret file in an editor with the .example as a starting point."
echo

restore_secret() {
  # restore_secret <example-in-repo> <real-target>
  local ex="$1" target="$2"
  if [[ -f "$ex" ]]; then
    echo ">>> $target  (template: $ex)"
    if confirm "    Edit $target now?"; then
      sudo cp "$ex" "$target"
      sudo "${EDITOR:-nano}" "$target"
    else
      echo "    Skipped — remember to create $target before starting the service."
    fi
  fi
}

restore_secret "$HERE/secrets/fr24feed.ini.example"  /etc/fr24feed.ini
restore_secret "$HERE/secrets/wg0.conf.example"      /etc/wireguard/wg0.conf

echo
echo "== NetworkManager (WiFi/IP) =="
echo "Static-IP/PSK connection templates are in configs/networkmanager/*.example"
echo "Either import them (filling in psk=) or just run: sudo raspi-config  → Network."
echo

echo "== enable services =="
for u in dnsmasq lighttpd readsb rtl_airband fr24feed sensor-server; do
  sudo systemctl enable "$u" 2>/dev/null && echo "  enabled $u" || echo "  (could not enable $u — installed?)"
done
sudo systemctl enable wlan-watchdog.timer 2>/dev/null || true

echo
echo "Done. Review the manual steps in README.md, then reboot and verify:"
echo "  systemctl status sensor-server readsb rtl_airband fr24feed dnsmasq lighttpd"
