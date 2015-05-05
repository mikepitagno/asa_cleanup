#!/usr/bin/python -tt

import sys

# Define lists for objects and object_groups and iterate through config looking for the string 'object network' and 'object-group network' ; Extract the name from the line and append to list if not already in the list
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

# Create object or object-group dictionary; Select each object from list and search each line in config for that object; If key(object) not found in dictionary populate dictionary with object and assign value of 1; If key is found, increment value by one 
def create_object_count(list, config_file):
  count = {}
  for i in list:
    for line in config_file:
      if i in line:
        if not i in count:
          count[i] = 1
        else:
          count[i] = count[i] + 1
  return count

# Create acl dictionary; Select each acl from list and search each line in config for that object; If key(object) not found in dictionary populate dictionary with object and assign value of 1; If key is found, increment value by one as long as line does not begin with 'access-list'
def create_acl_count(list, config_file):
  count = {}
  for i in list:
    for line in config_file:
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
  return count

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

# Main Program
def main():
  if len(sys.argv) == 2:
    f = open(sys.argv[1])
    config_file = f.readlines()	
    f.close()
  
    objects, object_groups, acls = create_list(config_file)
    
    object_count = create_object_count(objects, config_file)
    object_group_count = create_object_count(object_groups, config_file)
    acl_count = create_acl_count(acls, config_file)

#    print acl_count
#    print "\n"
#    print object_count
#    print "\n"
#    print object_group_count
#    print "\n"
    
    print "ACL Removal Lines:"
    create_conf(acl_count, 'acl')  
    print "\n"
    print "Object-Group Removal Lines:"
    create_conf(object_group_count, 'og')
    print "\n"
    print "Object Removal Lines:"
    create_conf(object_count, 'o')
    
  else:
    print "Config file missing.  Please include the full path of the ASA config file after the script."  

if __name__ == '__main__':
  main()
