# Secrets

**No real secrets live in this directory or anywhere in this repo.**

Only `*.example` files belong here. They are sanitised copies of the real config
files with every sensitive value replaced by `REPLACE_ME`. `capture.sh` generates
them automatically; `.gitignore` blocks the real (un-suffixed) versions so they
can't be committed by accident.

## Files

| Example file | Real file (on the Pi, NOT in repo) | Secret inside |
|--------------|-------------------------------------|---------------|
| `fr24feed.ini.example` | `/etc/fr24feed.ini` | `fr24key` |
| `wg0.conf.example` | `/etc/wireguard/wg0.conf` | `PrivateKey`, `PresharedKey` |
| `../configs/networkmanager/*.nmconnection.example` | `/etc/NetworkManager/system-connections/*` | WiFi `psk` |

## On a rebuild

`restore.sh` copies each `.example` to its real location and opens it in an editor
so you can paste the real secret in. See the main `README.md` for where to get each
value (regenerate WireGuard keys, re-enter fr24 key, etc.).

## If you ever accidentally commit a real secret

Rotate it immediately (it's now in git history): generate new WireGuard keys,
reset the fr24 key, change the WiFi password. Removing it from history is harder
than just invalidating the leaked value — so rotate first, scrub later.
