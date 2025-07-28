#!/usr/bin/env bash

set -e

# Install Python dependencies
if [[ -f "../requirements.txt" ]]; then
    pip install -r ../requirements.txt
fi

# Install Grafana (Debian/Ubuntu)
# This script uses the official Grafana APT repository.
# Modify as needed for other distributions.
if [[ "$EUID" -ne 0 ]]; then
  echo "Please run as root to install Grafana" >&2
  exit 1
fi

apt-get update
apt-get install -y apt-transport-https software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
apt-get update
apt-get install -y grafana

# Enable and start Grafana service
systemctl enable grafana-server
systemctl start grafana-server

echo "Grafana installation complete. Access it on port 3000."
