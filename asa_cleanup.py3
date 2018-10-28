#!/usr/bin/env python

'''
Name: asa_cleanup.py
Description: Cisco ASA Firewall Configuration Cleanup Script
Requires: Python 'sys' and 'ciscoconfparse' libraries

Example Usage (Linux Command Line):

~ $ asa_cleanup.py asa_config.cfg

Example Output:

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

'''

import sys
from ciscoconfparse import CiscoConfParse
import datetime
import os

class Element_Count:
    """Class to return dictionary with item / count pairs for each specified type (e.g. Group Policies, ACL's, Objects)"""
    
    def __init__(self, element, config_file):
        self.element = element
        self.config_file = config_file
    
    def gps(self):
        count = {}
        for i in self.element:
            for line in self.config_file:
                if line.startswith('group-policy'):
                    if not i in count:
                        count[i] = 1
                    else:
                        continue
                elif 'default-group-policy ' + i in line:
                    if not i in count:
                        count[i] = 1
                    else:
                        count[i] += 1
        return count
    
    def acl(self):
        count = {}
        for i in self.element:
            for line in self.config_file:
                if line.startswith('access-list'):
                    if not i in count:
                        count[i] = 1
                    else:
                        continue
                elif i in line:
                    if not i in count:
                        count[i] = 1
                    else:
                        count[i] += 1
        return count
    
    def obj(self):
        count = {}
        for k in self.element:
            count[k] = {}
            for v in self.element[k]:
                for line in self.config_file:
                    if v in line:  
                        if not v in count[k]:
                            count[k][v] = 1
                        else:
                            count[k][v] += 1
        return count

def id_elements(config_file):
    """"Create dictionaries for objects and object_groups and lists for acls and group-policies from ASA configuration file"""
    
    objects = {}
    object_groups = {}
    acls = []
    gps = []
    
    for line in config_file:
    
        if line.startswith('object '):
            k = line.split().pop(1)
            v = line.split().pop(2)
            if k not in objects:
                objects[k] = [v]
            else:
                objects[k].append(v)
    
        if line.startswith('object-group'):
            k = line.split().pop(1)
            v = line.split().pop(2)
            if k not in object_groups:
                object_groups[k] = [v]
            else:
                object_groups[k].append(v)
    
        if line.startswith('access-list'):
            acl = (line.split()).pop(1)
            if not acl in acls:
                acls.append(acl)
    
        if line.startswith('group-policy'):
            gp = (line.split()).pop(1)
            if gp == 'DfltGrpPolicy':
                continue
            elif not gp in gps:
                gps.append(gp)
    
    return (objects, object_groups, acls, gps)

def element_remove_list(element_count):
    """Create list of items (e.g. group policies, ACLs) to be removed; Takes list as input"""
    
    element_remove = []
    for element, count in list(element_count.items()):
        if count == 1:
            element_remove.append(element)
    return element_remove

def element_remove_dict(element_count):
    """Create dict of items (e.g. object, object_groups) to be removed; Takes dict as input"""
    
    element_remove = {}
    for k in element_count:
        element_remove[k] = []
        for element, count in list(element_count[k].items()):
            if count == 1:
                element_remove[k].append(element)
    return element_remove

def update_conf_list(element_remove, config_file, element_type):
    """Update config file with unused object-group, ACL, and group-policy statements removed; ciscoconfparse library needed to remove child objects"""
    
    parse = CiscoConfParse(config_file)
    
    for i in element_remove:
        for obj in parse.find_objects(r"^%s %s" % (element_type, i)):
                obj.delete(r"^%s %s" % (element_type, i))
    return generate_conf(parse)

def update_conf_dict(element_remove, config_file, element_type):
    """Update config file with unused object-group, ACL, and group-policy statements removed; ciscoconfparse library needed to remove child objects"""
    
    parse = CiscoConfParse(config_file)
    
    for k,v in list(element_remove.items()):
        element_type_new = element_type + " " + k
        for i in v:
            for obj in parse.find_objects(r"^%s %s" % (element_type_new, i)):
                obj.delete(r"^%s %s" % (element_type_new, i))
    return generate_conf(parse)

def generate_conf(parse):
    """Generate new config file"""
    
    config_file_new = []
    
    for line in parse.ioscfg:
        config_file_new.append(line)
    
    return config_file_new

def print_conf_list(element_remove, element_type):
    """Create removal statements from element lists"""
    for i in element_remove:
        print("clear configure %s %s" % (element_type, i))

def print_conf_dict(element_remove, element_type):
    """Create removal statements from element dictionaries"""
    for k,v in list(element_remove.items()):
        element_type_new = element_type + " " + k
        for i in v:
            print("no %s %s" % (element_type_new, i))

def main():
    """Start Main Program"""
    
    if len(sys.argv) == 2:
        f = open(sys.argv[1])
        config_name = os.path.basename(sys.argv[1]).split('.').pop(0)
        config_file = f.readlines()	
        f.close()
    
        # Global Variables
        global gp
        gp = "group-policy"
        global acl
        acl = "access-list"
        global obg
        obg = "object-group"
        global ob
        ob = "object"
    
        # Create lists or dicts of all items in config
        objects, object_groups, acls, gps = id_elements(config_file)
        # Create dict of group policies with number of times each appear in config 
        gp_count = Element_Count(gps, config_file).gps()
        # Create list of group policies to be removed
        gp_remove = element_remove_list(gp_count)
        # Update config file with group policies removed
        config_file = update_conf_list(gp_remove, config_file, gp)
        # Create dict of ACLs with number of times each appear in config 
        acl_count = Element_Count(acls, config_file).acl()
        # Create list of ACLs to be removed
        acl_remove = element_remove_list(acl_count)
        # Update config_file with ACLs removed
        config_file = update_conf_list(acl_remove, config_file, acl)
        # Create dict of object-groups with number of times each appear in config 
        object_group_count = Element_Count(object_groups, config_file).obj()
        # Create dict of object-groups to be removed
        object_group_remove = element_remove_dict(object_group_count)
        # Update config_file with object-groups removed
        config_file = update_conf_dict(object_group_remove, config_file, obg)
        # Create dict of objects with number of times each appear in config
        object_count = Element_Count(objects, config_file).obj()
        # Create dict of objects to be removed
        object_remove = element_remove_dict(object_count)
        # Update config_file with objects to be removed
        config_file = update_conf_dict(object_remove, config_file, ob)
    
        # Configure date format
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    
        # Create file with cleanup info
        sys.stdout=open("%s-CLEANUP-%s.txt" % (config_name,current_datetime), "w")
    
        print("Group Policy Removal Lines:")
        print_conf_list(gp_remove, gp)
    
        print("\n")
        print("ACL Removal Lines:")
        print_conf_list(acl_remove, acl)
    
        print("\n")
        print("Object-Group Removal Lines:")
        print_conf_dict(object_group_remove, obg)
    
        print("\n")
        print("Object Removal Lines:")
        print_conf_dict(object_remove, ob)
    
        sys.stdout.close()
    
        # Create New ASA config file
        sys.stdout=open("%s-NEW_CONFIG-%s.cfg" % (config_name,current_datetime), "w")
    
        for i in  config_file:
            print(i, end=' ')
    
        sys.stdout.close()
    
    else:
        print("Config file missing.  Please include the full path of the ASA config file after the script.")  
    
if __name__ == '__main__':
    main()
