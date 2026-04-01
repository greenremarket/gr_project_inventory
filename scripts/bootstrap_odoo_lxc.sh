#!/bin/bash
# Odoo 17 Enterprise bootstrap — Ubuntu 22.04 LXC (odoo-grm / CT 200)
# Run as root inside the container.
set -e

ODOO_DIR=/opt/odoo
ODOO_USER=odoo
PG_VERSION=16

echo "=== [1/8] System packages ==="
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  python3.10 python3.10-venv python3.10-dev python3-pip \
  git curl wget gnupg2 ca-certificates \
  build-essential libssl-dev libffi-dev \
  libxml2-dev libxslt1-dev libjpeg-dev libpng-dev zlib1g-dev \
  libsasl2-dev libldap2-dev libpq-dev \
  node-less npm \
  xfonts-75dpi xfonts-base fontconfig \
  nginx \
  default-mysql-client \
  default-libmysqlclient-dev \
  pkg-config

echo "=== [2/8] wkhtmltopdf 0.12.6 ==="
if ! command -v wkhtmltopdf &>/dev/null; then
  wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb -O /tmp/wkhtmltox.deb
  dpkg -i /tmp/wkhtmltox.deb || apt-get install -f -y -qq
  rm /tmp/wkhtmltox.deb
fi
wkhtmltopdf --version

echo "=== [3/8] odoo system user ==="
id $ODOO_USER &>/dev/null || useradd -m -d $ODOO_DIR -s /bin/bash $ODOO_USER

echo "=== [4/8] PostgreSQL odoo role ==="
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='odoo'\" | grep -q 1 || psql -c \"CREATE ROLE odoo WITH LOGIN CREATEDB PASSWORD 'odoo';\""

echo "=== [5/8] Directory structure ==="
mkdir -p $ODOO_DIR/{addons,enterprise,extra_addons,oca_addons,logs}
chown -R $ODOO_USER:$ODOO_USER $ODOO_DIR

echo "=== [6/8] Python virtualenv ==="
su - $ODOO_USER -c "python3.10 -m venv $ODOO_DIR/venv"
su - $ODOO_USER -c "$ODOO_DIR/venv/bin/pip install --upgrade pip wheel -q"

echo "=== [7/8] pymysql + fintech in venv (needed before Odoo requirements) ==="
su - $ODOO_USER -c "$ODOO_DIR/venv/bin/pip install pymysql>=1.1 -q"

echo "=== [8/8] nginx placeholder config ==="
cat > /etc/nginx/sites-available/odoo <<'NGINX'
upstream odoo {
    server 127.0.0.1:8069;
}
upstream odoochat {
    server 127.0.0.1:8072;
}
server {
    listen 80;
    server_name _;
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    location /longpolling {
        proxy_pass http://odoochat;
    }
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }
    location ~* /web/static/ {
        proxy_cache_valid 200 90d;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }
    gzip on;
    gzip_min_length 1100;
    gzip_buffers 4 32k;
    gzip_types text/plain application/x-javascript text/xml text/css;
}
NGINX
ln -sf /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "=== Bootstrap complete ==="
echo "Next: clone odoo + enterprise + modules, install pip requirements, create odoo.conf, systemd service."
