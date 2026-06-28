#!/usr/bin/env bash
#
# capture.sh — mirror the live Pi's service configs + systemd units into this repo.
# Re-runnable: run it any time you change a config on the Pi, then git commit.
#
# Secrets are NEVER copied verbatim. Files known to contain keys/passwords are
# copied to a *.example version with sensitive values blanked. Real secrets stay
# only on the Pi.
#
# Usage:  ./capture.sh            (run from the infrastructure/ dir, on the Pi)
#
set -euo pipefail

# Resolve repo paths relative to this script, regardless of where it's called from.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIGS="$HERE/configs"
SYSTEMD="$HERE/systemd"
SECRETS="$HERE/secrets"

mkdir -p "$CONFIGS"/{readsb,airband,dnsmasq,lighttpd,networkmanager} \
         "$SYSTEMD" "$SECRETS"

# --- helper: copy a file if it exists, preserving a note if it doesn't ----------
grab() {
  # grab <src> <dest>
  local src="$1" dest="$2"
  if sudo test -f "$src"; then
    sudo cp "$src" "$dest"
    sudo chown "$(id -u):$(id -g)" "$dest"
    echo "  ok   $src"
  else
    echo "  SKIP $src (not found)"
  fi
}

echo "== systemd units =="
# Your own / customised units. (Package-provided ones are listed too so a fresh
# Pi enables the same set; the restore guide re-enables them.)
for u in sensor-server.service wlan-watchdog.service wlan-watchdog.timer; do
  # These are likely your own custom units in /etc/systemd/system
  grab "/etc/systemd/system/$u" "$SYSTEMD/$u"
done

echo "== service configs =="
grab /etc/dnsmasq.conf              "$CONFIGS/dnsmasq/dnsmasq.conf"
# dnsmasq.d drop-ins, if you use them
if sudo test -d /etc/dnsmasq.d; then
  sudo cp -r /etc/dnsmasq.d "$CONFIGS/dnsmasq/dnsmasq.d" 2>/dev/null || true
  sudo chown -R "$(id -u):$(id -g)" "$CONFIGS/dnsmasq/dnsmasq.d" 2>/dev/null || true
  echo "  ok   /etc/dnsmasq.d/"
fi

grab /etc/default/readsb            "$CONFIGS/readsb/default-readsb"
grab /etc/lighttpd/lighttpd.conf    "$CONFIGS/lighttpd/lighttpd.conf"

# rtl_airband config path varies by install; try the common ones.
for f in /etc/rtl_airband.conf /usr/local/etc/rtl_airband.conf /etc/rtl_airband/rtl_airband.conf; do
  if sudo test -f "$f"; then grab "$f" "$CONFIGS/airband/rtl_airband.conf"; break; fi
done

echo "== package list =="
# Everything you've installed, so a fresh Pi can match. (Full list; restore guide
# notes which matter.)
dpkg --get-selections | awk '$2=="install"{print $1}' > "$HERE/packages.txt"
echo "  ok   packages.txt ($(wc -l < "$HERE/packages.txt") packages)"

echo "== SECRETS (sanitised → *.example) =="
# fr24feed.ini — blank the fr24key
if sudo test -f /etc/fr24feed.ini; then
  sudo sed -E 's/^(fr24key=).*/\1REPLACE_ME/' /etc/fr24feed.ini \
    | sudo tee "$SECRETS/fr24feed.ini.example" >/dev/null
  sudo chown "$(id -u):$(id -g)" "$SECRETS/fr24feed.ini.example"
  echo "  ok   fr24feed.ini.example (key blanked)"
fi

# WireGuard — blank PrivateKey and any PresharedKey
if sudo test -f /etc/wireguard/wg0.conf; then
  sudo sed -E 's/^(PrivateKey *=).*/\1 REPLACE_ME/; s/^(PresharedKey *=).*/\1 REPLACE_ME/' \
    /etc/wireguard/wg0.conf \
    | sudo tee "$SECRETS/wg0.conf.example" >/dev/null
  sudo chown "$(id -u):$(id -g)" "$SECRETS/wg0.conf.example"
  echo "  ok   wg0.conf.example (keys blanked)"
fi

# NetworkManager connection — capture the static-IP + powersave settings, blank PSK.
# We export the 'preconfigured' (wlan0) and wired connections as keyfiles.
for conn in "preconfigured" "Wired connection 1"; do
  src="/etc/NetworkManager/system-connections/${conn}.nmconnection"
  if sudo test -f "$src"; then
    safe_name="$(echo "$conn" | tr ' ' '_')"
    sudo sed -E 's/^(psk=).*/\1REPLACE_ME/' "$src" \
      | sudo tee "$CONFIGS/networkmanager/${safe_name}.nmconnection.example" >/dev/null
    sudo chown "$(id -u):$(id -g)" "$CONFIGS/networkmanager/${safe_name}.nmconnection.example"
    echo "  ok   ${safe_name}.nmconnection.example (psk blanked)"
  fi
done

echo
echo "Capture complete. Review changes, then:"
echo "  git add infrastructure/"
echo "  git status        # CONFIRM no real secrets staged"
echo "  git commit -m 'Update infrastructure snapshot'"
