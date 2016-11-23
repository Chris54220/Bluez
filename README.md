# Presence detection (Bluetooth 4.0 Low energy Beacon)

<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_TGVKU0VjZEdRV2M"/>	<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_cGRRTHJXa3ZXaHc"/>

# Objectif

Vérifiez la présence d'une liste de balises (BlueTooth Low Energy V4.0) et actualisez les uservariables en Domoticz en conséquence.
	
Nécessaire dans Domoticz, un uservariable de type Chaine pour chaque balise BlueTooth
	
<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_cHVIQVVlV1dVNDQ"/>
g
Le script fonctionne en 2 mode. Choisissez pour chaque balise celle que vous voulez:

- MODE REPEAT: Pour la balise dans la portée, mettez à jour l'uservariable toutes les 3 secondes avec le RSSI (signal de force) & "AWAY" autrement
- SWITCH_MODE: Pour la balise dans la portée, mettez à jour seulement 1 fois l'uservariable avec "HOME" & "AWAY" autrement.
	
	
La détection est très rapide: environ 4 secondes. Et l'absence est vérifiée toutes les 5 secondes en comparant l'heure de la dernière présence avec un temps mort pour chaque balise.


# Pourquoi
g
Vous pouvez utiliser ceci pour voir si une personne (qui porte toujours son / sa balise) est à la maison ou non, et déclenchez des événements basés sur ceci.

J'ai l'intention d'équiper toutes les clés de la famille avec la balise et automatiquement armer / désarmer mon système d'alarme Domoticz en vérifiant la présence d'une balise.
Domoticz déclenchera l'alarme lorsque le dernier balise quittera la maison.


# Matériel & balise

Adaptateur BlueTooth 	https://www.amazon.fr/gp/product/B014L88D64/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1
Balise			https://www.amazon.fr/gp/product/B01AUNMQMG/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1
	

# Instructions d'installation

Le script est hébergé ici	https://github.com/Chris54220/Bluez/tree/master/Presence-detection-beacon

# Bluez - la pile bluetooth linux

Commencez par installer les dépendances utilisées par la bibliothèque bluez.

	sudo apt-get update
	sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev

- Install Bluez

		git clone https://github.com/Chris54220/Bluez.git /home/pi/bluez
		cd bluez
		sudo ./configure --disable-systemd
		sudo make
		sudo make install
		sudo apt-get install python-bluez python-requests
		sudo cp attrib/gatttool /usr/local/bin/
		sudo chmod +x /usr/local/bin/gatttool
		sudo shutdown -r now
	
# Verif
	
Pour vous assurer que l'appareil USB Bluetooth est visible,

	lsusb 
	
Avec l'adaptateur enfichable montré ci-dessus, le résultat ressemblera à ceci:

	Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
	Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp.
	Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
	Bus 001 Device 004: ID 0658:0200 Sigma Designs, Inc.
	Bus 001 Device 005: ID 0403:6001 Future Technology Devices International, Ltd FT232 USB-Serial (UART) IC
	Bus 001 Device 006: ID 0463:ffff MGE UPS Systems UPS
	Bus 001 Device 007: ID 174c:5136 ASMedia Technology Inc.
	# Bus 001 Device 008: ID 0a12:0001 Cambridge Silicon Radio, Ltd Bluetooth Dongle (HCI mode)
	
Pour moi, l'adaptateur est celui sur le bus 001 Device 008, près de ma carte audio, RFXCOM, carte relais USB ... Pour afficher plus d'informations à ce sujet, faites:
	
	sudo lsusb -v -d 0a12:
	
Si cela fonctionne, exécutez l'outil hciconfig:

