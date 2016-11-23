#!/usr/bin/python
#   File : check_beacon_presence.py
#   Auteur: Christopher JOLLY
#   Date: 23-Nov-2016
#   Description : Vérifiez la présence d'une liste de balises (BlueTooth Low Energy V4.0) et mettez à jour les uservariables dans Domoticz en conséquence.
#   Version : 1.6
#
# Fonctionnalité : 
# Script s'occupe de l'adaptateur Bluetooth. Mettez-le en marche.
# Lorsque L'ADRESSE MAC d'une liste de balises est détectée, mettre à jour DOMOTICZ uservariable.
# Le script fonctionne maintenant en 2 mode. Choisissez pour chaque balise que vous voulez :
#       REPEAT MODE : Pour la balise dans la portée, Mettez à jour l'uservariable toutes les 3 secondes avec le RSSI & "AWAY" autrement.
#       SWITCH_MODE : Pour la balise dans la portée, Mettez à jour seulement une fois l'uservariable avec "HOME" & "AWAY" autrement.
# Envoyer "AWAY" lorsque les balises ne sont pas dans la plage.
# La détection est très rapide: environ 4 secondes. Et l'absence est vérifiée toutes les 5 secondes en comparant l'heure de la dernière présence avec un temps mort pour chaque balise.
#
#
# Obligatoire dans Domoticz: Un uservariable de type Chaîne pour chaque balise BLE
#
# Commande utile
# sudo /etc/init.d/check_beacon_presence [stop|start|restart|status] 
# 
# Configuration :
# Changez votre adresse IP et votre port ici :  
URL_DOMOTICZ = 'http://192.168.0.5:8080/json.htm?type=command&param=updateuservariable&idx=PARAM_IDX&vname=PARAM_NAME&vtype=2&vvalue=PARAM_CMD'
DOMOTICZ_USER='Bluez'
DOMOTICZ_PASS='8891'
						
REPEAT_MODE=1
SWITCH_MODE=0

#
# Configurez vos balises dans la table TAG_DATA avec: [Name,MacAddress,Timeout,0,idx,mode]
# Name : le nom de l'uservariable utilisé dans Domoticz
# macAddress : Adresse MAC
# Timeout est en secondes le temps écoulé sans une détection pour la commutation de la balise AWAY. C'est-à-dire: si votre balise émet tous les 3 à 8 seondes, un délai de 15 secondes semble bon.
# 0 : Utilisé par le script (Gardera l'heure de la dernière diffusion) 
# Idx de l'uservariable à Domoticz pour cette balise
# mode :
#		SWITCH_MODE = Une mise à jour par changement d'état 
#		REPEAT_MODE = Mise à jour continue du RSSI toutes les 3 secondes

TAG_DATA = [
            ["Tag_Bleu","5E:FF:56:A2:AF:15",15,0,15,REPEAT_MODE],
            ["Tag_Rouge","5E:FF:56:A2:AF:15",15,0,16,REPEAT_MODE],
			["Tag_Jaune","5E:FF:56:A2:AF:15",15,0,17,REPEAT_MODE]
           ]

           
import logging

### choose between DEBUG (log toutes les informations) ou WARNING (Changement d'état) ou CRITICAL (seulement erreur)
logLevel=logging.DEBUG
#logLevel=logging.CRITICAL
#logLevel=logging.WARNING

logOutFilename='/var/log/check_beacon_presence.log'  # LOG : File ou console (Commenter cette ligne sur la sortie de la console)
ABSENCE_FREQUENCY=5 								 # Fréquence du test d'absence. En seconde (Sans détection, commuter "AWAY".

################ Rien à éditer sous cette ligne #####################################################################################

import os
import subprocess
import sys
import struct
import bluetooth._bluetooth as bluez
import time
import requests
import signal
import threading


LE_META_EVENT = 0x3e
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02

def print_packet(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def handler(signum = None, frame = None):
    time.sleep(1)  #here check if process is done
    sys.exit(0)   
    
for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, handler)

def le_handle_connection_complete(pkt):
    status, handle, role, peer_bdaddr_type = struct.unpack("<BHBB", pkt[0:5])
    device_address = packed_bdaddr_to_string(pkt[5:11])
    interval, latency, supervision_timeout, master_clock_accuracy = struct.unpack("<HHHB", pkt[11:])
    #print "le_handle_connection output"
    #print "status: 0x%02x\nhandle: 0x%04x" % (status, handle)
    #print "role: 0x%02x" % role
    #print "device address: ", device_address

def request_thread(idx,cmd, name):
    try:
        url = URL_DOMOTICZ
        url=url.replace('PARAM_IDX',str(idx))
        url=url.replace('PARAM_CMD',str(cmd))
        url=url.replace('PARAM_NAME',str(name))
        result = requests.get(url,auth=(DOMOTICZ_USER, DOMOTICZ_PASS))
        logging.debug(" %s -> %s" % (threading.current_thread(), result))
    except requests.ConnectionError, e:
        logging.critical(' %s Request Failed %s - %s' % (threading.current_thread(), e, url) )

class CheckAbsenceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):

        time.sleep(ABSENCE_FREQUENCY)    
        for tag in TAG_DATA:
            elapsed_time_absence=time.time()-tag[3]
            if elapsed_time_absence>=tag[2] : # sleep execute after the first Home check.
                logging.warning('Tag %s not seen since %i sec => update absence',tag[0],elapsed_time_absence)
                threadReqAway = threading.Thread(target=request_thread,args=(tag[4],"AWAY",tag[0]))
                threadReqAway.start()

        while True:
            time.sleep(ABSENCE_FREQUENCY)
            for tag in TAG_DATA:
                elapsed_time_absence=time.time()-tag[3]
                if elapsed_time_absence>=tag[2] and elapsed_time_absence<(tag[2]+ABSENCE_FREQUENCY) :  #update when > timeout ant only 1 time , before the next absence check [>15sec <30sec]
                    logging.warning('Tag %s not seen since %i sec => update absence',tag[0],elapsed_time_absence)
                    threadReqAway = threading.Thread(target=request_thread,args=(tag[4],"AWAY",tag[0]))
                    threadReqAway.start()
            
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
if globals().has_key('logOutFilename') :
    logging.basicConfig(format=FORMAT,filename=logOutFilename,level=logLevel)
else:
    logging.basicConfig(format=FORMAT,level=logLevel)

#Reset Bluetooth interface, hci0
os.system("sudo hciconfig hci0 down")
os.system("sudo hciconfig hci0 up")

#Make sure device is up
interface = subprocess.Popen(["sudo hciconfig"], stdout=subprocess.PIPE, shell=True)
(output, err) = interface.communicate()

if "RUNNING" in output: #Check return of hciconfig to make sure it's up
    logging.debug('Ok hci0 interface Up n running !')
else:
    logging.critical('Error : hci0 interface not Running. Do you have a BLE device connected to hci0 ? Check with hciconfig !')
    sys.exit(1)
    
devId = 0
try:
    sock = bluez.hci_open_dev(devId)
    logging.debug('Connect to bluetooth device %i',devId)
except:
    logging.critical('Unable to connect to bluetooth device...')
    sys.exit(1)

old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
hci_toggle_le_scan(sock, 0x01)

for tag in TAG_DATA:
    tag[3]=time.time()-tag[2]  # initiate lastseen of every beacon "timeout" sec ago. = Every beacon will be AWAY. And so, beacons here will update 

th=CheckAbsenceThread()
th.daemon=True
th.start()

while True:
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    
    pkt = sock.recv(255)
    ptype, event, plen = struct.unpack("BBB", pkt[:3])

    if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            i =0
    elif event == bluez.EVT_NUM_COMP_PKTS:
            i =0 
    elif event == bluez.EVT_DISCONN_COMPLETE:
            i =0 
    elif event == LE_META_EVENT:
            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack("B", pkt[0])[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                            #logging.debug('UDID: ', print_packet(pkt[report_pkt_offset -22: report_pkt_offset - 6]))
                            #logging.debug('MAJOR: ', print_packet(pkt[report_pkt_offset -6: report_pkt_offset - 4]))
                            #logging.debug('MINOR: ', print_packet(pkt[report_pkt_offset -4: report_pkt_offset - 2]))
                            #logging.debug('MAC address: ', packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9]))
                            #logging.debug('Unknown:', struct.unpack("b", pkt[report_pkt_offset -2])) # don't know what this byte is.  It's NOT TXPower ?
                            #logging.debug('RSSI: %s', struct.unpack("b", pkt[report_pkt_offset -1])) #  Signal strenght !
                            macAdressSeen=packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                            for tag in TAG_DATA:
                                if macAdressSeen.lower() == tag[1].lower():  # MAC ADDRESS
                                    logging.debug('Tag %s Detected %s - RSSI %s - DATA unknown %s', tag[0], macAdressSeen, struct.unpack("b", pkt[report_pkt_offset -1]),struct.unpack("b", pkt[report_pkt_offset -2])) #  Signal strenght + unknown (hope it's battery life).                                    
                                    elapsed_time=time.time()-tag[3]  # lastseen
                                    if tag[5]==SWITCH_MODE and elapsed_time>=tag[2] : # Upadate only once : after an absence (>timeout). It's back again
                                        threadReqHome = threading.Thread(target=request_thread,args=(tag[4],"HOME",tag[0]))  # IDX, RSSI, name
                                        threadReqHome.start()
                                        logging.warning('Tag %s seen after an absence of %i sec : update presence',tag[0],elapsed_time)
                                    elif tag[5]==REPEAT_MODE and elapsed_time>3 : # in continuous, Every 2 sec
                                        rssi=''.join(c for c in str(struct.unpack("b", pkt[report_pkt_offset -1])) if c in '-0123456789')
                                        threadReqHome = threading.Thread(target=request_thread,args=(tag[4],rssi,tag[0]))   # IDX, RSSI, name
                                        threadReqHome.start()
                                        logging.debug('Tag %s is still there with an RSSI of %s  : update presence with RSSI',tag[0],rssi)
                                    tag[3]=time.time()   # update lastseen
                                    
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
