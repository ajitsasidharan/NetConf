'''
Program configures bgp peering on second node (dest_node) specified in the
input section.
This program works on the following assumptions -
    - Connectivity between both router loopbacks is working.
    The program doesn't try to correct/establish routing to loopback.
    - BGP router process in node 2 is absent or is configured with AS65000
    The program doesn't attempt to delete bgp configuration if it exists.
'''
#################Section: Imported modules#################
from ncclient import manager
import json
import xml.etree.ElementTree as ET
import sys
import xmltodict
import time
from bgpconfig import *
#################Input Section: Hard Coded Values used#################
native_ns       = "http://cisco.com/ns/yang/Cisco-IOS-XE-native"
ns_bgp          = 'http://cisco.com/ns/yang/Cisco-IOS-XE-bgp'
ns_bgp_oper     = 'http://cisco.com/ns/yang/Cisco-IOS-XE-bgp-oper'
source_node     = '1.1.1.1'
dest_node       = '2.2.2.2'
ibgp_as         = '65000'
netconf_port    = 830
user_name       = 'administrator'
pass_word       = 'CiscoDNA!'
input_file      = "input.txt"
wait_time       = '30'
lookup_data     = {"data": {"native": {"router": {"bgp": {"neighbor": {"id": source_node, "remote-as": ibgp_as},
                    "address-family": {"no-vrf": {"ipv4": {"af-name": "unicast", "ipv4-unicast": {"neighbor":{"id": source_node}}}}}}}}}}
#################Start of Code Implemenation#################
try:
    # Establish connection to both bgp peers. Quit if there are
    # issues with connection
    m=manager.connect(host=source_node, port=netconf_port,
                      username=user_name,password=pass_word,
                      device_params={'name':'csr'},
                      timeout=int(wait_time),hostkey_verify=False)
    m1=manager.connect(host=dest_node, port=netconf_port,
                       username=user_name,password=pass_word,
                       device_params={'name':'csr'},
                       timeout=int(wait_time),hostkey_verify=False)
except(Exception) as e:
    print("ERROR: Issue connecting to Nodes. Aborting bgp config.")
    print(e)
    quit()
# Get the bgp router configuration
result=m.get_config('running',get_bgp_router_filter(native_ns,ns_bgp))
# Print the original xml before modifications are done
print("\nINFO: Original XML: " + result.data_xml)
# Retrieve XML root
root = ET.fromstring(result.data_xml)
# Iterate through xml and make modifications as per json file
if (iterate_xml(root,lookup_data['data'])):
    print("INFO: XML modification successful")
else:
    print("ERROR: XML modification unsuccessful")
# Following lines take care of python version compatibility issues.
if (sys.version_info > (3, 0)):
    str = ET.tostring(root, encoding='unicode')
else:
    str = ET.tostring(root, encoding='utf-8')
# Convert the xml to a format that can used to configure network element
str=convert_to_config(str)
# Print the modified xml
print("\nINFO: Modified XML:",str)
# Edit the network element
try:
    m1.edit_config(target='running',config=str)
except Exception as e:
    print('ERROR: Configuration of node failed. Aborting')
    print(e)
    m.close_session()
    m1.close_session()
    quit()
print("INFO: Configuration successful.")
print("INFO: Waiting for " + wait_time + " seconds for bgp to come up")
time.sleep(int(wait_time))
bgp_state_info=m1.get(get_bgp_state_filter(ns_bgp_oper))
bgp_state_info_details=xmltodict.parse(bgp_state_info.xml)
bgp_connection_state=get_bgp_neighbor_state(bgp_state_info_details,source_node)
if bgp_connection_state == 'established':
    print("INFO: BGP connection is UP. Configurations successful")
elif bgp_connection_state is False:
    print("ERROR: Neighbor not found. Issues with retrieved config")
else:
    print("ERROR: BGP connection is DOWN. There is some issue with connectivity")
m.close_session()
m1.close_session()
