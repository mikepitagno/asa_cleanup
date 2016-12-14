#!/usr/bin/env python

'''
Name: asa_cleanup.py
Description: Cisco ASA Firewall Configuration Cleanup Script
Requires: Python 'sys' and 'ciscoconfparse' libraries

Example Usage (Linux Command Line):

~ $ asa_cleanup.py asa_config.cfg

Example Output:

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
'''

import sys
from ciscoconfparse import CiscoConfParse
import datetime
import os
    
class Item_Count:
    """Class to return dictionary with item / count pairs for each specified type (e.g. Group Policies, ACL's, Objects)
    """
    
    def __init__(self, list, config_file):
        self.list = list
        self.config_file = config_file
            
    def gps(self):
        count = {}
        for i in self.list:
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
        for i in self.list:
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
        for i in self.list:
            for line in self.config_file:    
                if i in line:
                    if not i in count:
                        count[i] = 1
                    else:
                        count[i] += 1
        return count
    

def create_list(config_file):
    """"Create lists for all objects, object_groups, acls and group-policies that exist within the provided configuration file"""
    
    objects = []
    object_groups = []
    acls = []
    gps = []
    
    for line in config_file:

        if 'object network ' in line:
            object = (line.split()).pop(2)
            if not object in objects:
                objects.append(object)
        
        if 'object-group network ' in line:
            object_group = (line.split()).pop(2)
            if not object_group in object_groups:
                object_groups.append(object_group)
        
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
    
def create_item_remove(item_count):
    """Create list of items (e.g. group policies, ACLs, object-groups, objects) to be removed"""
    
    item_remove = []
    
    for item, count in item_count.items():
        
        if count == 1:
            item_remove.append(item)

    return item_remove
    
# Update config file with unused object-group, ACL, and group-policy statements removed; ciscoconfparse library needed to remove child objects
def update_config_file_parse(item_remove, config_file, type):
  parse = CiscoConfParse(config_file)
  for i in item_remove:
    if type == 'obg':
      for obj in parse.find_objects(r"^object-group network %s" %i):
        obj.delete(r"^object-group network %s" %i)
    elif type == 'acl':
      for obj in parse.find_objects(r"^access-list %s" %i):
        obj.delete(r"^access-list %s" %i)
    elif type == 'gp':
      for obj in parse.find_objects(r"^group-policy %s" %i):
        obj.delete(r"^group-policy %s" %i)
  config_file_new = []
  for line in parse.ioscfg:
    config_file_new.append(line)
  return config_file_new
    
def create_conf(dict, type):
    """Iterate through object dictionary and print keys that have a value of 1 (i.e. are not used anywhere in the config)"""

    for i in dict.keys():
        
        if dict[i] == 1:
            if type == 'o':
                print "no object network %s" % (i)
            elif type == 'og':
                print "no object-group network %s" % (i)
            elif type == 'acl':
                print "clear configure access-list %s" % (i)
            elif type == 'gp':
                print "clear configure group-policy %s" % (i)             
   
def main():
    """Start Main Program"""

    if len(sys.argv) == 2:
        f = open(sys.argv[1])
        config_name = os.path.basename(sys.argv[1]).split('.').pop(0)
        config_file = f.readlines()	
        f.close()
    
        # Create lists of all items in config
        objects, object_groups, acls, gps = create_list(config_file)
        
        # Create dict(gp_count) of group policies(keys) with number of times each appear in config(values); 
        # Create list(gp_remove) of group policies to be removed; Update config file with group policies removed
        gp_count = Item_Count(gps, config_file).gps()
        gp_remove = create_item_remove(gp_count)
        config_file = update_config_file_parse(gp_remove, config_file, 'gp')
    
        # Create dict(acl_count) of ACLs(keys) with number of times each appear in config(values); 
        # Create list(acl_remove) of ACLs to be removed; Update config_file with ACLs removed
        acl_count = Item_Count(acls, config_file).acl()
        acl_remove = create_item_remove(acl_count)
        config_file = update_config_file_parse(acl_remove, config_file, 'acl')
    
        # Create dict(object_group_count) of object-groups(keys) with number of times each appear in config(values); 
        # Create list(object_group_remove) of object-groups to be removed; Update config_file with object-groups removed
        object_group_count = Item_Count(object_groups, config_file).obj()
        object_group_remove = create_item_remove(object_group_count)
        config_file = update_config_file_parse(object_group_remove, config_file, 'obg')

        # Create list of objects to remove    
        object_count = Item_Count(objects, config_file).obj()
           
        # Configure date format
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        
        # Open file to pass print output
        sys.stdout=open("%s-CLEANUP-%s.txt" % (config_name,current_datetime), "w")
            
        print "Group Policy Removal Lines:"
        create_conf(gp_count, 'gp')  
        
        print "\n"
        print "ACL Removal Lines:"
        create_conf(acl_count, 'acl')  
        
        print "\n"
        print "Object-Group Removal Lines:"
        create_conf(object_group_count, 'og')
        
        print "\n"
        print "Object Removal Lines:"
        create_conf(object_count, 'o')
        
        sys.stdout.close()
         
    else:
        print "Config file missing.  Please include the full path of the ASA config file after the script."  
    
if __name__ == '__main__':
  main()
