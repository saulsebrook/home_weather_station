# Pi Infrastructure — Rebuild Guide

This directory is a living mirror of the weather-station Pi's service configuration:
the Flask sensor server, ADS-B (readsb/tar1090), rtl_airband/Icecast, fr24feed,
dnsmasq, lighttpd, WireGuard, the static-IP network setup, and the wlan watchdog.

It lets you rebuild the whole box on fresh hardware. It is **~90% automated** —
the remaining manual steps are the things that genuinely cannot live in a repo
(private keys, the WiFi password, dongle serials). Those are listed at the bottom.

---

## Layout

| Path | What it is |
|------|------------|
| `capture.sh` | Re-runnable. Pulls live configs from the Pi into this repo and blanks secrets. Run it after any config change, then commit. |
| `restore.sh` | Copies these configs onto a fresh Pi and re-enables services. Prompts for the secrets. |
| `packages.txt` | Full apt package list captured from the working Pi. |
| `configs/` | Service config files (dnsmasq, readsb, airband, lighttpd, NetworkManager). |
| `systemd/` | Custom systemd units (sensor-server, wlan-watchdog). |
| `secrets/` | **`*.example` placeholders only.** Real secrets never live here. |

---

## To capture the current Pi's state (run on the existing Pi)

```bash
cd ~/weather-station/infrastructure   # adjust to your repo path
./capture.sh
git add infrastructure/
git status        # ← LOOK: confirm no real secret files are staged
git commit -m "Update infrastructure snapshot"
git push
```

`capture.sh` only ever writes `*.example` versions of secret-bearing files, and
`.gitignore` blocks the real ones. But always eyeball `git status` before committing.

---

## To rebuild on a fresh Pi

1. **Flash Raspberry Pi OS** (same major version — note this Pi's: run `cat /etc/os-release` and record it).
2. **Clone the repo** onto the new Pi.
3. **Install packages:**
   ```bash
   sudo apt update
   # core set — see packages.txt for the full list
   sudo apt install -y dnsmasq lighttpd wireguard
   # readsb, rtl_airband, fr24feed: install per their own upstream instructions
   # (they're not in standard apt repos)
   ```
4. **Run the restore script:**
   ```bash
   cd infrastructure
   ./restore.sh
   ```
   It copies configs into place, then stops to prompt you for each secret.
5. **Do the manual steps below.**
6. **Reboot and verify** each service: `systemctl status sensor-server readsb rtl_airband fr24feed dnsmasq lighttpd wlan-watchdog.timer`

---

## Irreducible manual steps (cannot be in the repo)

These must be redone by hand on a new Pi:

- **WiFi password** — re-enter the PSK when restoring the NetworkManager connection,
  or just set up WiFi via `raspi-config`. (Real lesson learned: this Pi runs better
  on **Ethernet** — the onboard BCM43430 wedges. Strongly consider wiring the rebuild.)
- **Static IP** — the configs set `192.168.1.133`. Confirm that suits the new network.
- **WireGuard keys** — generate a new keypair (`wg genkey | tee privatekey | wg pubkey > publickey`),
  paste the private key into `/etc/wireguard/wg0.conf`, and update the **peer** (your
  other end) with the new public key.
- **fr24feed key** — paste your existing `fr24key` into `/etc/fr24feed.ini`, or
  re-run `sudo fr24feed --signup` for a new one.
- **RTL-SDR dongle serials** — this setup expects two dongles with serials `ADSB`
  and `AIRBAND`. Set them on the new dongles with `rtl_eeprom -s ADSB` / `-s AIRBAND`,
  or edit the configs to match whatever serials your dongles have.
- **ESP8266 sensor nodes** — they POST to the Pi's IP. If the IP changes, re-flash
  the node firmware (in this repo) with the new address. If the IP stays `192.168.1.133`,
  nothing to do.

---

## Notes

- `packages.txt` is the *full* installed list for reference; you don't need every
  package, but it's the ground truth if something's missing.
- The wlan-watchdog only matters on WiFi (it bounces `wlan0`). On Ethernet it's a
  harmless dormant safety net.
