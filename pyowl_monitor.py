#!/usr/bin/env python3
# Python Logger for Owl Intuition, setup to read electricity and solar readings
import socket
import requests
import struct
import xml.etree.ElementTree as ET
from datetime import datetime

# Reference: https://pymotw.com/3/socket/multicast.html
multicast_group = '224.192.32.19'
server_address = ('', 22600)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

class OwlMonitor(object):
    def __init__(self):
        self.isMonitoring = False
        self.currentReadings = {"time": 0, "consuming": -1, "exporting": 0, "generating": -1}
        self.dayReadings = {"consumed": -1, "exported":-1, "generated": -1}
        self.startMonitoring()

    def printStatus(self):
        # Current
        consuming = int(float(self.currentReadings["consuming"]))
        exporting = int(float(self.currentReadings["exporting"]))
        generating = int(float(self.currentReadings["generating"]))

        # Daily
        consumed = int(float(self.dayReadings["consumed"]))
        exported = int(float(self.dayReadings["exported"]))
        generated = int(float(self.dayReadings["generated"]))

        timestamp = datetime.fromtimestamp(int(self.currentReadings["time"]))

        currentStatus = "Current Usage: %d W, (Mains: %s W, Solar: %s W) [%s]" % ((consuming - generating), consuming, generating, timestamp)
        dayStatus = "Daily Usage - Consumed: (%s), Exported: (%s), Generated: (%s)" % (consumed, exported, generated)

        if ((consuming == -1) or (generating == -1)):
            print("Awaiting Owl readings...")
        else:
            print(currentStatus)
            print(dayStatus)

    def startMonitoring(self):
        if not self.isMonitoring:
            self.isMonitoring = True

        print('\nOwl monitoring began at: %s' % (datetime.now()))
        while self.isMonitoring:
            data, address = sock.recvfrom(1024)

            xml_root = ET.fromstring(data)

            if xml_root.tag == "solar":
                """
                timestamp {}
                current {}
                    generating {'units': 'w'}
                    exporting {'units': 'w'}
                """
                solar_entry = {}
                
                for child in xml_root:
                    if child.tag == "timestamp":
                        entry_time = child.text
                    
                        solar_entry["time"] = entry_time
                    
                    if child.tag == "current":
                        for current_child in child:
                            solar_entry[current_child.tag] = current_child.text

                    if child.tag == "day":
                        for current_child in child:
                            if current_child.tag == "generated":
                                self.dayReadings["generated"] = current_child.text
                            if current_child.tag == "exported":
                                self.dayReadings["exported"] = current_child.text

                self.currentReadings["time"] = solar_entry["time"]
                self.currentReadings["generating"] = solar_entry["generating"]
                self.currentReadings["exporting"] = solar_entry["exporting"]
                

            if xml_root.tag == "electricity":
                """
                timestamp {}
                property {}
                    <current>
                        <watts>355.00</watts>
                        <cost>1.46</cost>
                    </current>
                """
                electricity_entry = {}
                
                for child in xml_root:
                    
                    if child.tag == "timestamp":
                        entry_time = child.text
                        electricity_entry["time"] = entry_time

                    if child.tag == "property":
                        for property_child in child:
                            if property_child.tag == "current":
                                for current_child in property_child:
                                    electricity_entry[current_child.tag] = current_child.text
                            if property_child.tag == "day":
                                for current_child in property_child:
                                    if current_child.tag == "wh":
                                        self.dayReadings["consumed"] = current_child.text

                #print(electricity_entry)
                self.currentReadings["time"] = electricity_entry["time"]
                self.currentReadings["consuming"] = electricity_entry["watts"]

            self.printStatus()

owlMonitor = OwlMonitor()       
