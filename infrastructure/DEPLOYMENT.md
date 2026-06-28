# Weather Station + ADS-B Pi — Deployment Guide

A Raspberry Pi running a home environmental sensor network alongside aviation
data services (ADS-B aircraft tracking, VHF airband audio streaming, and flight
data feeding). This document explains every component, how to deploy the whole
stack to fresh hardware, and where each piece comes from upstream.

---

## 1. What this box does

```
                    ┌──────────────────────────────────────────────┐
   ESP8266 nodes    │                Raspberry Pi                  │
   ┌──────────┐     │                                              │
   │ INSIDE   │─POST─┤► Flask sensor server (Gunicorn) ─► *.jsonl  │
   │ OUTSIDE  │─POST─┤  :5000                                       │
   │ GARAGE   │─POST─┤                                              │
   └──────────┘     │   lighttpd ─► reverse proxy + tar1090 web    │
                    │                                              │
   RTL-SDR "ADSB" ──┤► readsb ─► tar1090 (map)  ─► fr24feed        │
   RTL-SDR "AIRBAND"┤► rtl_airband ─► Icecast (audio stream)       │
                    │                                              │
                    │   dnsmasq (.lan DNS)   WireGuard (VPN)        │
                    │   wlan-watchdog (self-heal)                  │
                    └──────────────────────────────────────────────┘
```

The Pi has a **static IP `192.168.1.133`** and hostname **`weather.lan`**.
Two RTL-SDR V4 dongles are distinguished by EEPROM serial: `ADSB` and `AIRBAND`.

> **Hardware lesson learned:** the onboard BCM43430 WiFi intermittently wedges its
> receive path under load. This box runs far more reliably on **Ethernet**. The
> `wlan-watchdog` exists to auto-recover when WiFi *must* be used. Wire it if you can.

---

## 2. Components & packages

### Your application
| Component | What it is | Config / location |
|-----------|-----------|-------------------|
| **Flask sensor server** | Python app that receives JSON POSTs from the ESP8266 nodes, appends to per-node `.jsonl` files, serves the dashboard, and exposes the airband/ATC tabs. Run under **Gunicorn** (`-w 4`). | `sensor_server.py`, unit `systemd/sensor-server.service` |
| **ESP8266 node firmware** | Arduino sketches (one per node) reading a BME280 over I²C, POSTing temp/humidity/pressure on a ~5-min deep-sleep cycle with a 3-attempt retry loop. | `firmware/` in repo |
| **wlan-watchdog** | Bash script + systemd timer that bounces `wlan0` if all sensor `.jsonl` files go stale for 15 min — recovers the WiFi-wedge condition. | `systemd/wlan-watchdog.{service,timer}`, `/usr/local/bin/wlan-watchdog.sh` |

### Third-party services
| Package | Purpose | Default port | Config file | Upstream |
|---------|---------|--------------|-------------|----------|
| **readsb** | Decodes Mode-S/ADS-B from the SDR into aircraft tracks; outputs Beast (30005), SBS/Basestation (30003), and JSON for the map. | 30005 / 30003 / 8080 | `/etc/default/readsb` | https://github.com/wiedehopf/readsb |
| **tar1090** | Web map front-end for readsb (the live aircraft map). | served via lighttpd | (installed alongside readsb) | https://github.com/wiedehopf/tar1090 |
| **rtl_airband** | Demodulates VHF airband (AM) audio from the second SDR and streams it. | feeds Icecast | `/etc/rtl_airband.conf` | https://github.com/charlie-foxtrot/RTLSDR-Airband |
| **Icecast** | Audio streaming server that serves the rtl_airband output to browsers/players. | 8000 | `/etc/icecast2/icecast.xml` | https://icecast.org |
| **fr24feed** | Flightradar24 feeder client; takes readsb's Beast output (127.0.0.1:30005) and uploads to FR24. | 8754 (status) | `/etc/fr24feed.ini` | https://www.flightradar24.com/share-your-data |
| **dnsmasq** | Lightweight local DNS; resolves `.lan` hostnames (e.g. `weather.lan`) on the LAN. | 53 | `/etc/dnsmasq.conf` (+ `/etc/dnsmasq.d/`) | https://thekelleys.org.uk/dnsmasq/doc.html |
| **lighttpd** | Web server; reverse-proxies the Flask app and serves the tar1090 map. | 80 | `/etc/lighttpd/lighttpd.conf` | https://www.lighttpd.net |
| **WireGuard** | VPN for remote access to the Pi. Subnet `10.222.127.0/24`. | 51820/udp | `/etc/wireguard/wg0.conf` | https://www.wireguard.com |
| **Gunicorn** | WSGI server running the Flask app with 4 workers. | 5000 (behind lighttpd) | in `sensor-server.service` | https://gunicorn.org |

> `readsb`, `tar1090`, `rtl_airband`, and `fr24feed` are **not in the standard apt
> repos** — each installs from its own project (links above). The rest are apt packages.

---

## 3. Config file details

### `/etc/default/readsb`
Controls the readsb daemon: which SDR device (by serial `ADSB`), gain, your
receiver lat/lon, and which network output ports to open. The Beast output on
**30005** is what fr24feed consumes. *(See `configs/readsb/default-readsb` for the
exact captured flags.)*

### `/etc/rtl_airband.conf`
Defines the airband SDR (serial `AIRBAND`), the VHF frequencies to demodulate, and
the Icecast mountpoint(s) it streams to. *(See `configs/airband/rtl_airband.conf`.)*

### `/etc/fr24feed.ini`
The FR24 feeder config. Key fields: `receiver="beast-tcp"` pointing at
`127.0.0.1:30005` (readsb), and your **`fr24key`** (a secret — held only on the Pi,
blanked in the repo's `.example`).

### `/etc/dnsmasq.conf` (+ `/etc/dnsmasq.d/`)
Serves local DNS so `weather.lan` and other `.lan` names resolve on the network.
Also used for WireGuard-side DNS resolution. *(See `configs/dnsmasq/`.)*

### `/etc/lighttpd/lighttpd.conf`
Fronts the stack on port 80: reverse-proxies the Gunicorn app (`:5000`) and serves
the tar1090 map. *(See `configs/lighttpd/lighttpd.conf`.)*

### NetworkManager connections
`configs/networkmanager/*.example` hold the static-IP (`192.168.1.133`) setup for
both the wired connection and `preconfigured` (wlan0), including the WiFi
power-save-disabled setting. The WiFi `psk` is blanked.

---

## 4. Deploying to a fresh Pi

### Prerequisites
- Raspberry Pi OS flashed (match the major version — check the old Pi with
  `cat /etc/os-release`).
- Network reachable; ideally **wired Ethernet** (see the WiFi note above).
- Two RTL-SDR V4 dongles.

### Step 1 — clone the repo
```bash
cd ~
git clone https://github.com/saulsebrook/home_weather_station.git weather-station
cd weather-station
```

### Step 2 — install apt packages
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv gunicorn \
                    dnsmasq lighttpd icecast2 wireguard git
```
(The full captured package list is in `infrastructure/packages.txt` for reference.)

### Step 3 — install the non-apt services
Follow each upstream installer:
- **readsb + tar1090** — wiedehopf's one-line installers (see repos above).
- **rtl_airband** — build per RTLSDR-Airband docs.
- **fr24feed** — `sudo bash -c "$(wget -O - https://repo-feed.flightradar24.com/install_fr24_amd64.sh)"`
  (use the ARM/Pi variant from their share-your-data page).

### Step 4 — set the SDR dongle serials
The configs expect serials `ADSB` and `AIRBAND`:
```bash
rtl_eeprom -d 0 -s ADSB
rtl_eeprom -d 1 -s AIRBAND
```
(Re-plug after writing EEPROM.)

### Step 5 — run the restore script
```bash
cd infrastructure
./restore.sh
```
This copies all configs into place, installs the systemd units, and prompts you to
paste each **secret** (it never stores them):
- WireGuard `PrivateKey` (regenerate: `wg genkey | tee privatekey | wg pubkey > publickey`)
- fr24 `fr24key`
- WiFi `psk` (or just use `sudo raspi-config`)

### Step 6 — Python deps & app
```bash
cd ~/weather-station
pip install -r requirements.txt --break-system-packages   # or in a venv
```

### Step 7 — enable & start everything
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dnsmasq lighttpd icecast2 readsb rtl_airband \
                            fr24feed sensor-server wlan-watchdog.timer
sudo systemctl enable --now wg-quick@wg0
```

### Step 8 — verify
```bash
systemctl status sensor-server readsb rtl_airband fr24feed dnsmasq lighttpd icecast2
curl -s localhost:5000 | head        # Flask app responding
vcgencmd get_throttled               # want 0x0 (power healthy)
```
Then load `http://192.168.1.133/` in a browser for the dashboard and map.

---

## 5. Irreducible manual steps (can't be in the repo)

| Thing | Why manual | How |
|-------|-----------|-----|
| WireGuard private key | Secret; per-host | `wg genkey` → paste into `wg0.conf`; update peer with new public key |
| fr24 key | Account secret | Paste existing, or `sudo fr24feed --signup` |
| WiFi password | Secret | `restore.sh` prompt, or `raspi-config` |
| SDR serials | Hardware EEPROM | `rtl_eeprom -s ADSB` / `-s AIRBAND` |
| ESP node target IP | Flashed into firmware | Re-flash nodes if Pi IP changes from `192.168.1.133` |

---

## 6. Keeping the repo in sync

Whenever you change a config on the Pi, re-mirror it:
```bash
cd ~/weather-station/infrastructure
./capture.sh
cd ~/weather-station
git add infrastructure/ && git status   # confirm no real secrets
git commit -m "Update infrastructure snapshot" && git push
```

---

## 7. Service quick-reference

| Service | Check | Restart |
|---------|-------|---------|
| Flask app | `systemctl status sensor-server` | `sudo systemctl restart sensor-server` |
| ADS-B | `systemctl status readsb` · map at `/tar1090` | `sudo systemctl restart readsb` |
| Airband | `systemctl status rtl_airband` | `sudo systemctl restart rtl_airband` |
| FR24 feed | `http://192.168.1.133:8754` | `sudo systemctl restart fr24feed` |
| DNS | `systemctl status dnsmasq` | `sudo systemctl restart dnsmasq` |
| Watchdog | `cat /var/log/wlan-watchdog.log` | `sudo systemctl restart wlan-watchdog.timer` |
| VPN | `sudo wg show` | `sudo systemctl restart wg-quick@wg0` |
