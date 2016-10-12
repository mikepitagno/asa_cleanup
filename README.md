## ASA Cleanup

### Introduction

A Python command line script to identify unused access-lists, object-groups and objects within a Cisco ASA firewall configuration file.  The script will also dynamically modify the config file during execution to prevent having to run it multiple times. For example, if an ACL marked for removal renders an object-group no longer necessary, the script will also mark that object-group for removal on the same run.

Update (2016-10-12): Added support to cleanup unused group policies; Output now printed to file.

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
clear configure group-policy TEST_GP  
clear configure group-policy TEST_GP2

ACL Removal Lines:  
clear configure access-list TEST_ACL  
clear configure access-list TEST2_ACL

Object-Group Removal Lines:  
no object-group network TEST_OBJECT_GROUP  
no object-group network TEST2_OBJECT_GROUP

Object Removal Lines:  
no object network TEST_OBJECT  
no object network TEST2_OBJECT  
