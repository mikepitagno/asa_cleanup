#!/usr/bin/python -tt

import sys

# Define lists for objects and object_groups and iterate through config looking for the string 'object network' and 'object-group network' ; Extract the name from the line and append to list if not already in the list
def create_object_list(config_file):
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
def create_object_count(objects, config_file):
  object_count = {}
  for i in objects:
    for line in config_file:
      if i in line:
        if not i in object_count:
          object_count[i] = 1
        else:
          object_count[i] = object_count[i] + 1
  return object_count

# Create object-group dictionary; Select each object from list and search each line in config for that object; If key(object) not found in dictionary populate dictionary with object and assign value of 1; If key is found, increment value by one 
def create_object_group_count(object_groups, config_file):
  object_group_count = {}
  for i in object_groups:
    for line in config_file:
      if i in line:
        if not i in object_group_count:
          object_group_count[i] = 1
        else:
          object_group_count[i] = object_group_count[i] + 1
  return object_group_count

# Iterate through object dictionary and print keys that have a value of 1 (i.e. are not used anywhere in the config)
def create_object_conf(object_count):
  for i in object_count.keys():
    if object_count[i] == 1:
      print "no object network %s" % (i)

# Iterate through object-group dictionary and print keys that have a value of 1 (i.e. are not used anywhere in the config)  
def create_object_group_conf(object_group_count):  
  for i in object_group_count.keys():
    if object_group_count[i] == 1:
      print "no object-group network %s" % (i)

def main():
  f = open(sys.argv[1])
  config_file = f.readlines()	
  f.close()
  
  objects, object_groups = create_object_list(config_file)
    
  object_count = create_object_count(objects, config_file)
  object_group_count = create_object_group_count(object_groups, config_file)
  
  print "\n"
  print "Object Removal Lines:"
  create_object_conf(object_count)
  print "\n"
  print "Object-Group Removal Lines:"
  create_object_group_conf(object_group_count)
  
if __name__ == '__main__':
  main()
