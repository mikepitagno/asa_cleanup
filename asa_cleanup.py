#!/usr/bin/python -tt

import sys
from ciscoconfparse import CiscoConfParse

# Create lists for all objects, object_groups, acls and group-policies that exist within the provided configuration file
def create_list(config_file):
  objects = []
  object_groups = []
  acls = []
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
  return (objects, object_groups, acls)

# Create object or object-group dictionary 'count' from corresponding list created in 'create_list' function where dictionary keys are object or object-group names and values are the number of times they appear in the config
# Create acl dictionary; Select each acl from list and search each line in config for that object; If key(object) not found in dictionary populate dictionary with object and assign value of 1; If key is found, increment value by one as long as line does not begin with 'access-list'
def create_item_count(list, config_file, type):
  count = {}
  for i in list:
    for line in config_file:
      if type == 'acl':
        if line.startswith('access-list'):
          if not i in count:
            count[i] = 1
          else:
            continue
        elif i in line:
          if not i in count:
            count[i] = 1
          else:
            count[i] = count[i] + 1
      elif type == 'ob' or type == 'obg':
        if i in line:
          if not i in count:
            count[i] = 1
          else:
            count[i] = count[i] + 1
  return count

# Create list of items to be removed(e.g. ACLs, object-groups); This list will be imported into function 'update_config_file' to remove these lines from the config_file; Updated config_file will be used by object and object-group removal to prevent having to run program a second time after ACLs have been removed
def create_item_remove(item_count):
  item_remove = []
  for item, count in item_count.items():
    if count == 1:
      item_remove.append(item)
  return item_remove

# Update config file with ACL lines removed
def update_config_file(item_remove, config_file):
  for i in item_remove:  
    for line in config_file:
      if i in line and line.startswith('access-list '):
        config_file.remove(line)
      else:
        continue
  return config_file

# Update config file with object-group lines removed; ciscoconfparse library needed to remove child objects
def update_config_file_parse(item_remove, config_file, type):
  parse = CiscoConfParse(config_file)
  for i in item_remove:
    if type == 'obg':
      for obj in parse.find_objects(r"^object-group network %s" %i):
        obj.delete(r"^object-group network %s" %i)
    elif type == 'acl':
      for obj in parse.find_objects(r"^access-list %s" %i):
        obj.delete(r"^access-list %s" %i)
  config_file_new = []
  for line in parse.ioscfg:
    config_file_new.append(line)
  return config_file_new

# Iterate through object dictionary and print keys that have a value of 1 (i.e. are not used anywhere in the config)
def create_conf(dict, type):
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

# Main Program
def main():
  if len(sys.argv) == 2:
    f = open(sys.argv[1])
    config_file = f.readlines()	
    f.close()
    
    # Create Lists of all items in config
    objects, object_groups, acls = create_list(config_file)
    
    # Create dict(acl_count) of ACLs(keys) with number of times each appear in config(values); Create list(acl_remove) of ACLs to be removed; Update config_file with ACLs removed
    acl_count = create_item_count(acls, config_file, 'acl')
    acl_remove = create_item_remove(acl_count)
    config_file = update_config_file_parse(acl_remove, config_file, 'acl')
    
    # Create dict(object_group_count) of object-groups(keys) with number of times each appear in config(values); Create list(object_group_remove) of object-groups to be removed; Update config_file with object-groups removed
    object_group_count = create_item_count(object_groups, config_file, 'obg')
    object_group_remove = create_item_remove(object_group_count)
    config_file = update_config_file_parse(object_group_remove, config_file, 'obg')
   
    object_count = create_item_count(objects, config_file, 'ob')

    print "\n"
    print "ACL Removal Lines:"
    create_conf(acl_count, 'acl')  
    print "\n"
    print "Object-Group Removal Lines:"
    create_conf(object_group_count, 'og')
    print "\n"
    print "Object Removal Lines:"
    create_conf(object_count, 'o')
    print "\n"   
 
  else:
    print "Config file missing.  Please include the full path of the ASA config file after the script."  

if __name__ == '__main__':
  main()
