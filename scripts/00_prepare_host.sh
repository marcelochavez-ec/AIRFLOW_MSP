#!/usr/bin/env bash
set -euo pipefail

sudo dnf -y update
sudo dnf -y install \
  curl \
  firewalld \
  openssh-server \
  policycoreutils-python-utils \
  dnf-plugins-core

sudo systemctl enable --now firewalld sshd

if ! id admin >/dev/null 2>&1; then
  sudo useradd -m -s /bin/bash admin
fi

echo "admin:marce" | sudo chpasswd
echo "root:marce" | sudo chpasswd
echo "admin ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/90-admin >/dev/null
sudo chmod 0440 /etc/sudoers.d/90-admin

sudo tee /etc/ssh/sshd_config.d/90-airflow-admin.conf >/dev/null <<'EOF'
PasswordAuthentication yes
AllowUsers admin
EOF
sudo systemctl restart sshd

sudo install -d -o admin -g admin -m 0755 /home/marcelo.chavez/airflow
sudo install -d -o admin -g admin -m 0775 \
  /home/marcelo.chavez/airflow/dags \
  /home/marcelo.chavez/airflow/logs \
  /home/marcelo.chavez/airflow/plugins \
  /home/marcelo.chavez/airflow/config \
  /home/marcelo.chavez/airflow/deploy
sudo chown -R 50000:0 /home/marcelo.chavez/airflow/{dags,logs,plugins,config}

sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8088/tcp
sudo firewall-cmd --reload

sudo semanage fcontext -a -t container_file_t "/home/marcelo\.chavez/airflow(/.*)?"
sudo restorecon -Rv /home/marcelo.chavez/airflow
