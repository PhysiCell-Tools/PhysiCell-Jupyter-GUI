import xml.etree.ElementTree as ET
import sys

xml_hier_file = "PhysiCell_settings.xml"
xml_flat_file = "tmp2.xml"
argc = len(sys.argv)
print('argc=',argc)
if argc == 3:
    xml_hier_file = sys.argv[1]
    xml_flat_file = sys.argv[2]
elif argc > 3:
    print('Error: too many args. Only 1 allowd (optional):  [.xml config file]')

# The original, hierarchical XML
print("\n\n     ------- parsing ",xml_hier_file)
tree_hier = ET.parse(xml_hier_file)
root_hier = tree_hier.getroot()

# The newly constructed, expanded (flattened) XML
tree_flat = ET.parse(xml_flat_file)
root_flat = tree_flat.getroot()
cell_defs_flat = root_flat.find("cell_definitions")

num_nodes = 0
#for node in root.iter():
for node in []:
  print(node)
  num_nodes += 1
#print("num_nodes=",num_nodes)

print('----- recursive -----')
prefix = ""
full_path = ""
last_tag = ""
# root_cell_def = xml_root.find("cell_definitions//cell_definition")
cell_defs_hier = root_hier.find("cell_definitions")
def print_children(parent):
    global cell_def_name, prefix, full_path, last_tag #, len_leaf_text
    for child in parent:
        if child.tag == 'cell_definition':
            cell_def_name = child.attrib['name']
            print("==== cell_def_name=",cell_def_name,'\n')

        print(prefix,child.tag,child.attrib)
        full_path += '//' + child.tag
        # full_path += '//' + child.tag
        last_tag = child.tag
        print('full_path=',full_path)
    # print(child.attrib)
        prefix = prefix + "--"
        print_children(child)
#  prefix = prefix - "--"
    #-----------------------------
    # Reached a leaf element at this point. Update the corresponding element in the new, expanded XML.
    # full_path = full_path[0:len(full_path)-len(last_tag)-2]
    # print("   leaf path=",full_path[2:])
    try:
        leaf_text = cell_defs_hier.find(full_path[2:]).text
        leaf_text = leaf_text.strip('\n')
        leaf_text = leaf_text.strip('\t')
        leaf_text = leaf_text.strip()
        print('    leaf_text=',leaf_text)
        len_leaf_text = len(leaf_text)
        print('    len_leaf_text=',len_leaf_text)

        # Update the expanded XML
        leaf_text2 = cell_defs_flat.find(full_path[2:]).text
        print('    leaf_text2=',leaf_text2)
        if (len_leaf_text > 0):
            find_str = full_path[2:]
            new_str = "cell_definition[@name='" + cell_def_name + "']"
            print("    new_str=",new_str)
            find_str = find_str.replace("cell_definition",  new_str)
            print("  *** find_str=",find_str)
            print("  *** for cell_def_name ",cell_def_name,": replace ",cell_defs_flat.find(find_str).text," with ", leaf_text)
            # cell_defs_flat.find(find_str).text = leaf_text
            cell_defs_flat.find(find_str).text = cell_defs_hier.find(find_str).text
    except:
        pass
    try:
        idx = full_path.rindex("//")  # strip off the last element
        full_path = full_path[0:idx]
    except:
        pass
    print("~~~ popped out: full_path=",full_path)
    
    # root_cell_def = xml_root.find("cell_definitions + ")

    prefix = prefix[2:]

# print_children(root)
print_children(cell_defs_hier)

new_xml_file = "tmp3.xml"
print("---> ",new_xml_file)
tree_flat.write(new_xml_file)

sys.exit(1)

print('-----------------------')
for child in root_hier:
  print(child.tag)
  for child2 in child:
    print('--',child2.tag)
    for child3 in child2:
      print('----',child3.tag)
      for child4 in child3:
        print('------',child4.tag)
#  print(child.tag, child.attrib)
