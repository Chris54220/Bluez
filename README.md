# Presence detection (Bluetooth 4.0 Low energy Beacon)

<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_TGVKU0VjZEdRV2M"/>	<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_cGRRTHJXa3ZXaHc"/>

# Objectif

	Vérifiez la présence d'une liste de balises (BlueTooth Low Energy V4.0) et actualisez les uservariables en Domoticz en conséquence.
	
	Nécessaire dans Domoticz, un uservariable de type Chaine pour chaque balise BlueTooth
	
<img src="https://drive.google.com/uc?id=0BwsyidAGqsS_cHVIQVVlV1dVNDQ"/>

Le script fonctionne en 2 mode. Choisissez pour chaque balise celle que vous voulez:

	MODE REPEAT: Pour la balise dans la portée, mettez à jour l'uservariable toutes les 3 secondes avec le RSSI (signal de force) & "AWAY" autrement
	
	SWITCH_MODE: Pour la balise dans la portée, mettez à jour seulement 1 fois l'uservariable avec "HOME" & "AWAY" autrement.
	
	
La détection est très rapide: environ 4 secondes. Et l'absence est vérifiée toutes les 5 secondes en comparant l'heure de la dernière présence avec un temps mort pour chaque balise.


# Pourquoi

Vous pouvez utiliser ceci pour voir si une personne (qui porte toujours son / sa balise) est à la maison ou non, et déclenchez des événements basés sur ceci.

J'ai l'intention d'équiper toutes les clés de la famille avec la balise et automatiquement armer / désarmer mon système d'alarme Domoticz en vérifiant la présence d'une balise.
Domoticz déclenchera l'alarme lorsque le dernier balise quittera la maison.


# Matériel & balise

	Adaptateur BlueTooth 	https://www.amazon.fr/gp/product/B014L88D64/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1
	
	Balise					https://www.amazon.fr/gp/product/B01AUNMQMG/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1
	

# Instructions d'installation

Le script est hébergé ici	https://github.com/Chris54220/Bluez/tree/master/Presence-detection-beacon
