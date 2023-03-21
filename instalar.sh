#!/bin/bash

#instalar dependencias
pip install dbus-next==0.2.3

# descargar repo
mkdir proyecto
cd proyecto
git clone https://github.com/edwing335/prueba_tecnica.git

cd prueba_tecnica

#enviar scripts
sudo cp ./servidor.py /usr/local/bin
sudo cp ./config.ini /usr/local/bin
sudo chmod 777 /usr/local/bin/servidor.py
sudo chmod 777 /usr/local/bin/config.ini

sudo cp ./servicio_py.sh /usr/local/bin
sudo chmod 777 /usr/local/bin/servicio_py.sh

sudo cp ./servicio_py.service /etc/systemd/system
sudo chmod 777 /etc/systemd/system/servicio_py.service

#recargar el servicio daemon:
sudo systemctl daemon-reload

#habilitamos:
sudo systemctl enable servicio_py.service

#iniciamos servicio
sudo systemctl start servicio_py.service





