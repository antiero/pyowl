#!/usr/bin/env python3
# Python Logger for Owl Intuition, setup to read electricity and solar readings
import socket
import struct
import xml.etree.ElementTree as ET
import datetime
import csv

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

while True:
    print('\nWaiting to receive Owl message...')
    data, address = sock.recvfrom(1024)

    xml_root = ET.fromstring(data)
    
    if xml_root.tag == "solar":
        print("SOLAR READING")
    
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

        print(solar_entry)
        
        with open("/Users/ant/solar.csv", "a", newline="") as solar_csv_file:
            writer = csv.DictWriter(solar_csv_file, delimiter=',', fieldnames = ['time', 'generating', 'exporting'])
            writer.writerow(solar_entry)

    elif xml_root.tag == "electricity":
        """
        timestamp {}
        property {}
            <current>
                <watts>355.00</watts>
                <cost>1.46</cost>
            </current>
        """
        print("ELECTRICITY READING")
        
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

        print(electricity_entry)

        with open("/Users/ant/electicity.csv", "a", newline="") as elec_csv_file:
            writer = csv.DictWriter(elec_csv_file, delimiter=',', fieldnames = ['time', 'watts', 'cost'])
            writer.writerow(electricity_entry)
