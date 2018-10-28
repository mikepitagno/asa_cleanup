## ASA Cleanup

### Introduction

A Python command line script to identify unused access-lists, object-groups and objects within a Cisco ASA firewall configuration file.  The script will also dynamically modify the config file during execution to prevent having to run it multiple times. For example, if an ACL marked for removal renders an object-group no longer necessary, the script will also mark that object-group for removal on the same run.

Update (2016-10-12): Added support to cleanup unused group policies; Output now printed to file.

Update (2018-10-28): Added support for different object and object_group types (e.g. network, service, protocol, icmp-type); Previously script would only parse network types; Script now outputs updated configuration file (.cfg) in addition to file with recommended changes (.txt). 

### Installation Notes / Prerequisites

Python2 Version - asa_cleanup.py  
Python3 Version - asa_cleanup_v3.py

**CiscoConfParse Required**
Debian/Ubuntu based install:
```
sudo apt-get install python-pip
sudo pip install ciscoconfparse
```

### Usage
```
asa_cleanup.py 'CONFIG_FILE'
```

### Sample Output

Group Policy Removal Lines:  
clear configure group-policy GRP1  
clear configure group-policy GRP2  

ACL Removal Lines:  
clear configure access-list ACL1  
clear configure access-list ACL2  

Object-Group Removal Lines:  
no object-group network NETOBJECTGRP1  
no object-group network NETOBJECTGRP2  
no object-group service SERVOBJECTGRP1  
no object-group service SERVOBJECTGRP2  
no object-group icmp-type ICMPOBJECTGRP1  
no object-group protocol PROTOCOLGRP1  

Object Removal Lines:  
no object network NETOBJECT1  
no object network NETOBJECT2  
no object service SERVOBJECT1  
no object service SERVOBJECT2  
