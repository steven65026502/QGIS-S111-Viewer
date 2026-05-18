# S-111 Droplet 部署手冊

目標：把 `s111_verification` 資料庫與 S-111 hotspot API 放到 Ubuntu Droplet，讓學長前端可以透過 HTTP 呼叫 API。

目前 API 是 Flask，不是 FastAPI。正式部署使用：

```text
PostgreSQL + PostGIS
Flask + Gunicorn
Nginx
```

## 0. 建議 Droplet

| 項目 | 建議 |
| --- | --- |
| OS | Ubuntu 22.04 LTS |
| RAM | 2GB 起跳 |
| Disk | 50GB 內建硬碟 |
| Region | Singapore |

目前資料庫約 7.5GB，50GB 硬碟先夠用。若查詢變慢或多人使用，再升級到 4GB RAM。

## 1. 連上 Droplet

從你的電腦用 PowerShell：

```powershell
ssh root@DROPLET_IP
```

把 `DROPLET_IP` 換成 DigitalOcean 給你的 IP。

## 2. 安裝系統套件

在 Droplet 上執行：

```bash
apt update
apt upgrade -y
apt install -y postgresql postgresql-contrib postgis postgresql-14-postgis-3 python3-venv python3-pip nginx ufw
```

如果 Ubuntu 套件版本不是 PostgreSQL 14，可以先查：

```bash
apt-cache search postgresql | grep postgis
```

然後安裝對應版本的 `postgresql-XX-postgis-3`。

## 3. 建立資料庫與帳號

先進 PostgreSQL：

```bash
sudo -u postgres psql
```

在 psql 裡執行，密碼請改成你自己的強密碼：

```sql
CREATE DATABASE s111_verification;
CREATE USER s111_app WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';
\c s111_verification
CREATE EXTENSION IF NOT EXISTS postgis;
GRANT CONNECT ON DATABASE s111_verification TO s111_app;
GRANT USAGE ON SCHEMA public TO s111_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO s111_app;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO s111_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO s111_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO s111_app;
\q
```

## 4. 上傳資料庫 dump

你可以用 WinSCP、SFTP，或 PowerShell 的 `scp`。

範例：

```powershell
scp "G:\我的雲端硬碟\geojson\S111_給學長_完整交付版_全部資料\03_資料庫交接文件\s111_verification_20260504.dump" root@DROPLET_IP:/tmp/s111_verification.dump
```

## 5. 還原資料庫

在 Droplet 上執行：

```bash
sudo -u postgres pg_restore --clean --if-exists --no-owner -d s111_verification /tmp/s111_verification.dump
```

還原後補權限：

```bash
sudo -u postgres psql -d s111_verification -c "GRANT USAGE ON SCHEMA public TO s111_app;"
sudo -u postgres psql -d s111_verification -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO s111_app;"
sudo -u postgres psql -d s111_verification -c "GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO s111_app;"
```

確認大小與筆數：

```bash
sudo -u postgres psql -d s111_verification -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
sudo -u postgres psql -d s111_verification -c "SELECT COUNT(*) FROM hotspot_points;"
```

## 6. 上傳 API 程式

建議放在 `/opt/s111_viewer`。

在 Droplet 上：

```bash
mkdir -p /opt/s111_viewer
```

從你的電腦上傳 `06_API服務` 裡的檔案，或用 WinSCP 放到 `/opt/s111_viewer`。

最少需要：

```text
scripts/s111_api_server.py
requirements_api.txt
deploy/s111-api.service
deploy/nginx_s111_api.conf
```

建立服務用帳號：

```bash
useradd --system --home /opt/s111_viewer --shell /usr/sbin/nologin s111api
chown -R s111api:www-data /opt/s111_viewer
```

## 7. 建立 Python 環境

```bash
cd /opt/s111_viewer
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_api.txt
deactivate
chown -R s111api:www-data /opt/s111_viewer
```

測試 Flask API 可否連 DB：

```bash
cd /opt/s111_viewer
S111_DB_HOST=127.0.0.1 \
S111_DB_PORT=5432 \
S111_DB_NAME=s111_verification \
S111_DB_USER=s111_app \
S111_DB_PASSWORD='CHANGE_ME_STRONG_PASSWORD' \
.venv/bin/python scripts/s111_api_server.py --host 127.0.0.1 --port 8111
```

另開一個 SSH 視窗測試：

```bash
curl http://127.0.0.1:8111/api/status
```

測完可按 `Ctrl+C` 停掉手動模式。

## 8. 設定環境變數

```bash
mkdir -p /etc/s111
cp /opt/s111_viewer/deploy/s111-api.env.example /etc/s111/s111-api.env
nano /etc/s111/s111-api.env
```

把密碼改成真正的 DB 密碼：

```text
S111_DB_PASSWORD=你的強密碼
```

保護密碼檔：

```bash
chown root:www-data /etc/s111/s111-api.env
chmod 640 /etc/s111/s111-api.env
```

## 9. 設定 Gunicorn systemd 服務

```bash
cp /opt/s111_viewer/deploy/s111-api.service /etc/systemd/system/s111-api.service
systemctl daemon-reload
systemctl enable --now s111-api
systemctl status s111-api
```

看 log：

```bash
journalctl -u s111-api -f
```

本機測試：

```bash
curl http://127.0.0.1:8111/api
curl "http://127.0.0.1:8111/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=5"
```

## 10. 設定 Nginx

```bash
cp /opt/s111_viewer/deploy/nginx_s111_api.conf /etc/nginx/sites-available/s111-api
ln -sf /etc/nginx/sites-available/s111-api /etc/nginx/sites-enabled/s111-api
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

開防火牆：

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

從瀏覽器測：

```text
http://DROPLET_IP/api
```

Threshold hotspot：

```text
http://DROPLET_IP/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000
```

## 11. Pipeline 連線策略

建議不要把 PostgreSQL 的 `5432` 直接開給全世界。

比較安全的做法是 SSH tunnel。你在 Windows 開一個 PowerShell：

```powershell
ssh -L 15432:127.0.0.1:5432 root@DROPLET_IP
```

再讓本機 pipeline 連：

```powershell
$env:S111_DB_HOST = "127.0.0.1"
$env:S111_DB_PORT = "15432"
$env:S111_DB_NAME = "s111_verification"
$env:S111_DB_USER = "s111_app"
$env:S111_DB_PASSWORD = "你的強密碼"
```

這樣資料會透過 SSH 寫進 Droplet 的 PostgreSQL，不需要對外開 DB 連接埠。

## 12. 常用檢查指令

API 狀態：

```bash
systemctl status s111-api
journalctl -u s111-api -n 100 --no-pager
```

Nginx 狀態：

```bash
systemctl status nginx
tail -n 100 /var/log/nginx/s111-api.error.log
```

資料庫大小：

```bash
sudo -u postgres psql -d s111_verification -c "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

資料表筆數：

```bash
sudo -u postgres psql -d s111_verification -c "SELECT COUNT(*) FROM hotspot_points;"
```

## 13. 目前限制

- API 目前回傳 `hotspot_points` 的超標點，不是完整全格點資料。
- `/api/hotspot-series` 只會回傳該點在 hotspot 表中存在的時間，不代表完整 24 小時所有值。
- 若未來前端需要完整曲線或完整熱度圖，需要新增完整格點資料表。
