#!/usr/bin/python -tt

import sys

# Define lists for objects and object_groups and iterate through config looking for the string 'object network' and 'object-group network' ; Extract the name from the line and append to list if not already in the list
def create_list(config_file):
  objects = []
  object_groups = []
  for line in config_file:
    if 'object network ' in line:
      object = (line.split()).pop(2)
      if not object in objects:
        objects.append(object)
    if 'object-group network ' in line:
      object = (line.split()).pop(2)
      if not object in object_groups:
        object_groups.append(object)
  return (objects, object_groups)

# Create object dictionary; Select each object from list and search each line in config for that object; If key(object) not found in dictionary populate dictionary with object and assign value of 1; If key is found, increment value by one 
def create_count(list, config_file):
  count = {}
  for i in list:
    for line in config_file:
      if i in line:
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

# Main Program
def main():
  if len(sys.argv) == 2:
    f = open(sys.argv[1])
    config_file = f.readlines()	
    f.close()
  
    objects, object_groups = create_list(config_file)
    
    object_count = create_count(objects, config_file)
    object_group_count = create_count(object_groups, config_file)
  
    print "\n"
    print "Object Removal Lines:"
    create_conf(object_count, 'o')
    print "\n"
    print "Object-Group Removal Lines:"
    create_conf(object_group_count, 'og')
  else:
    print "Config file missing.  Please include the full path of the ASA config file after the script."  

if __name__ == '__main__':
  main()
