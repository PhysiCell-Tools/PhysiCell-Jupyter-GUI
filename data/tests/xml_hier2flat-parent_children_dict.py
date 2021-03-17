# xml_hier2flat.py - convert a hierarchical PhysiCell_settings.xml (with inheritance 
#                    of <cell_definitions>) into one without inheritance, i.e., 
#                    each <cell_definition> is "flattened" (expanded to be complete).
#                    
# Usage:
# $ python xml_hier2flat.py <hierarchical XML>
#
# Author: Randy Heiland
#

import xml.etree.ElementTree as ET
import sys
import string

prefix = ""
full_path = ""
last_tag = ""

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

def recurse_update_cell_def(xml_hier_file, xml_flat_file, out_xml_file):
    # The original, hierarchical XML
    print("\n\n     ------- parsing ",xml_hier_file)
    tree_hier = ET.parse(xml_hier_file)
    root_hier = tree_hier.getroot()

    # The newly constructed, expanded (flattened) XML
    # shutil.copy(xml_hier_file, xml_flat_file)
    tree_flat = ET.parse(xml_flat_file)
    root_flat = tree_flat.getroot()
    cell_defs_flat = root_flat.find("cell_definitions")

    num_nodes = 0
    #for node in root.iter():
    # for node in []:
    #     print(node)
    #     num_nodes += 1
    #print("num_nodes=",num_nodes)

    print('----- recursive -----')
    prefix = ""
    full_path = ""
    last_tag = ""
    # root_cell_def = xml_root.find("cell_definitions//cell_definition")
    cell_defs_hier = root_hier.find("cell_definitions")


    # print_children(root)
    print_children(cell_defs_hier)

    print("---> ",out_xml_file)
    tree_flat.write(out_xml_file)

#========================================================================

xml_file = "PhysiCell_settings.xml"
argc = len(sys.argv)
print('argc=',argc)
if argc == 2:
    xml_file = sys.argv[1]
elif argc > 2:
    print('Error: too many args. Only 1 allowd (optional):  [.xml config file]')
#print('argv=',sys.argv)

"""
For example:
	<cell_definitions>
		<cell_definition name="A" ID="0" visible="true">
			<p1>0</p1>
			<p2>42</p2>
			<p3>43</p3>
			<custom_data>
				<x>A</x> 
			</custom_data>
		</cell_definition>
		<cell_definition name="A1" ID="1" parent_type="A">
			<p1>1</p1>
			<custom_data>
				<x>A1</x> 
			</custom_data>
		</cell_definition>
"""

#--------------------------------------------------
print("\n--- Phase 0: Build cell_defs_dict: {cell_def_name : {'ID':value, 'parent':value}, ...} \n\
         and parent_children_dict: {parent_cell_def_name : [child1, child2, ...], ...}")

tree = ET.parse(xml_file)  
xml_root = tree.getroot()

# "cell_def" will be a dict with key = cell_def name, value = {'ID':value, 'parent':value}
cell_defs_dict = {}
parent_children_dict = {}
children_list = []

cell_defs = tree.find('cell_definitions')
print('cell_defs =',cell_defs)
for cd in list(cell_defs):
    print(cd.attrib)
    attrib_dict = {}
    attrib_dict['ID'] = cd.attrib['ID']

    if 'parent_type' in cd.attrib.keys():
        attrib_dict['parent'] = cd.attrib['parent_type']
    else:
        attrib_dict['parent'] = None

    # if 'parent_type' in cd.attrib.keys():
    #     children_list.append(cd.attrib['name'])
    #     attrib_dict['parent'] = cd.attrib['parent_type']
    #     parent_children_dict[cd.attrib['parent_type']] = children_list
    # else:
    #     attrib_dict['parent'] = None
    #     parent_children_dict[cd.attrib['name']] = None
    cell_defs_dict[cd.attrib['name']] = attrib_dict

print('\n cell_defs_dict= ',cell_defs_dict)  
kv = list(cell_defs_dict.items())
print('\n kv (a list)=',kv)
# for cd in cell_defs_dict:
for cd in kv:
    # print(type(cd[1]))
    print('cd[0] = ',cd[0])
    id_parent = list(cd[1].values()) 
    print('id_parent= ', id_parent)
    if id_parent[1]:  # is there a parent?
        print(' -- id_parent[1] =', id_parent[1])
        print('    (before)parent_children_dict= ',parent_children_dict)  
        # parent_children_dict[cd[0]] = id_parent[1]
        if (id_parent[1] in parent_children_dict.keys()):
            parent_children_dict[id_parent[1]].append(cd[0])
        else:
            # parent_children_dict[id_parent[1]] = list(cd[0])
            parent_children_dict[id_parent[1]] = [cd[0]]
        print('    (after)parent_children_dict= ',parent_children_dict)  

        # if (parent_children_dict[id_parent[1]]):
        #     parent_children_dict[id_parent[1]].append(cd[0])
        # else:
        #     parent_children_dict[id_parent[1]] = []
        
    # if cd.values['parent']:
        # print(' found parent for ',cd.values['parent'])

print('\n parent_children_dict= ',parent_children_dict,'\n')  

xml_root = tree.getroot()
sys.exit()
#--------------------------------------------------
print("\n--- Phase 1: Remove all <cell_definition> nodes with a 'parent_type' attribute.")
cell_defs = tree.find('cell_definitions')
for cd in list(cell_defs):
    # print(cell_def.tag, cell_defs_dict.attrib['name'])
    print(cd.attrib)
    print(cd.attrib.keys())
    if ('parent_type' in cd.attrib.keys()):
        print("--- removing ", cd.attrib['name'])
        cell_defs.remove(cd)

new_xml_file = "tmp1.xml"
print("---> ",new_xml_file)
tree.write(new_xml_file)
# sys.exit()

#--------------------------------------
print("\n--- Phase 2: For each child of 'parent_type', make a copy of its parent.")
# tree = ET.parse("tmp1.xml")  
tree = ET.parse(new_xml_file)  
xml_root = tree.getroot()
cell_defs = tree.find('cell_definitions')
print('cell_defs=',cell_defs)
root_cell_def = xml_root.find("cell_definitions//cell_definition")
root_name = root_cell_def.attrib['name'] 
print("   root_name = ",root_name)
# print("--- Insert duplicate root cell_def for of its children")
cd_vals = list(cell_defs_dict.values())
print("cd_vals = ",cd_vals)

for cd in cd_vals:
    if cd['parent'] == root_name:   # handles just the children of root (not grandchildren, etc)
        print('inserting child of ',root_name)
        # root_cell_def.attrib['ID'] = cd['ID']
        cell_defs.insert(0,root_cell_def)
        # root_cell_def.attrib['name'] = 'bar'
        # child = xml_root.find("cell_definitions//cell_definition[2]")
#sys.exit()
#cell_def_all = tree.findall('cell_definition')

new_xml_file = "tmp2.xml"
# new_xml_file = "flat.xml"
print("---> ",new_xml_file)
tree.write(new_xml_file)

# sys.exit()
#--------------------------------------
print("\n--- Phase 3: Rename those suckers.")
tree = ET.parse(new_xml_file)  
xml_root = tree.getroot()
cell_defs = tree.find('cell_definitions')

idx_rename = 1  # rename those cell_def after the root/parent (which has idx=0)

idx = 1
# for cd in cell_defs.findall('cell_definition'):
for cdv in cd_vals:
    # print('cell_def=',cd)
    # print('cd name, ID =',cd.attrib['name'], cd.attrib['ID'])
    # print('cdv =',cdv)

    # cd_vals = list(cell_defs_dict.values())
    # print('cd_vals = ',cd_vals)
    if cdv['parent'] == root_name:   # 'A'
        # cd.attrib['ID'] = cdv['ID']
        idx += 1
        # cell_defs.find('cell_definition[' + str(idx) + ']').attrib['ID'] = cdv['ID']
        cd_str = 'cell_definition[' + str(idx) + ']'
        print('updating cd_str=',cd_str,' with ID=',cdv['ID'])
        cell_defs.find(cd_str).attrib['ID'] = cdv['ID']

# NB! Need to save the file at this point and read it back in to continue processing.
new_xml_file = "tmp3.xml"
print("---> ",new_xml_file)
tree.write(new_xml_file)

# cell_def_all = tree.findall('cell_definition')
# print('cell_def_all=',cell_def_all)

# recurse_update_cell_def(xml_hier_file, xml_flat_file, out_xml_file):
# recurse_update_cell_def(xml_file, "tmp3.xml", "final.xml")
sys.exit()
#--------------------------------------------
tree = ET.parse("tmp1.xml")  
xml_root = tree.getroot()
idx = 1
cd_keys = list(cell_defs_dict.keys())
for cd in cd_vals:
    # if cd['parent'] == root_name:   # handles just the children of root (not grandchildren, etc)
    if cd['parent']:
    # if cd.values()['parent'] == root_name:
        new_name = cd_keys[idx]
        new_ID = cd['ID']
        idx += 1
        # new_name = 'bar' + str(idx)
        print('renaming child of ',root_name,' to be ',new_name, 'with ID ',new_ID)
        xml_root.find("cell_definitions//cell_definition[" +str(idx) + "]").attrib['name'] = new_name
        xml_root.find("cell_definitions//cell_definition[" +str(idx) + "]").attrib['ID'] = new_ID
        # break
        # print(xml_root.find("cell_definitions//cell_definition[" + str(idx) + "]"))

new_xml_file = "tmp2.xml"
# new_xml_file = "flat.xml"
print("---> ",new_xml_file)
tree.write(new_xml_file)

sys.exit()
#--------------------------------------------------
# tree = ET.parse("new_flat_config1.xml")  
# cell_defs = tree.find('cell_definitions')
# xml_root = tree.getroot()

# print("--- Change cell_def name for *each* leaf")
# idx = -1
# leaf_name = list(leaf_cell_defs.keys())
# for cell_def in list(cell_defs):
#     if idx >= 0:
#         cell_def.attrib['name'] = leaf_name[idx]
#         cell_def.attrib['ID'] = leaf_cell_defs[leaf_name[idx]]
#         cell_def.set("parent","default")  # insert parent = "default" attribute

#         print(cell_def.attrib['name'])
#     idx += 1

# new_xml_file = "new_flat_config1.xml"
# tree.write(new_xml_file)
# print("\nDone. Please check the output file: " + new_xml_file + "\n")

#--------------------------------------------------
# We want to replace all the XML elements and attributes in the (copied) parent's with the
# newly defined values provided by its children.
#
print("\n===================================================================================")
print("--- Phase 2: update all children's elements and attributes.")

"""
for example:
    		<cell_definition name="A1" ID="1" parent_type="A">
			<p1>1</p1>
			<custom_data>
				<x>A1</x> 
			</custom_data>
"""

tree_flat = ET.parse("tmp2.xml")  
xml_flat_root = tree_flat.getroot()

sys.exit()

#------------------------------------------------------------

idx = -1
# tree_orig = ET.parse("PhysiCell_settings.xml")  
tree_orig = ET.parse(xml_file)  
# tree = ET.parse("new_flat_config1.xml")  
xml_orig = tree_orig.getroot()
uep = None
# for requested cell_def param values in the original (inheritance) XML, copy them into the new (flattened) XML
for cd in xml_orig.findall('cell_definitions//cell_definition'):
    idx += 1
    if cd.attrib["name"] == "immune":  # we only want the "immune" cell def
        uep = cd
        print("---------------- processing immune cell_def at idx= ",idx)   # 2  (0=default, 1=lung epi)
        # immune_uep = root.find('.//cell_definitions')
        for child in cd:
            if child.tag != 'custom_data':
                print("------- calling recurse_node on child=",child)
                recurse_node(child,"","")  # should only call with child=<phenotype>, then recursively calls its children
print("\nDone.")

new_xml_file = "new_flat_config2.xml"
tree_flat.write(new_xml_file)
print("\nDone. Please check the output file: " + new_xml_file + "\n")

sys.exit()
#--------------------------------------------------
print("\n===================================================================================")
print("--- Phase 3: edit the new .xml so each immune cell type has its specific params (from the ORIGINAL .xml).")

tree_orig = ET.parse("PhysiCell_settings.xml")  
xml_orig = tree_orig.getroot()

tree_flat = ET.parse("new_flat_config2.xml")  
# tree_flat = ET.parse(new_xml_file)  
xml_flat_root = tree_flat.getroot()  # we'll update xml_flat_root (and write to a new output file)

def update_this_immune_cell_def_params(xmlpath, save_param_val, cell_def_name):
#    for cell_def in immune_cell_defs:
    for cd in xml_flat_root.findall('cell_definitions//cell_definition'):  # find *this* cell_def in flattened XML
        if cd.attrib['name'] == cell_def_name:
            if len(xmlpath) > 13:  # i.e., not equal to just "//custom_data" (with no param name)
                print('-- update ',cell_def_name, ', xmlpath=',xmlpath, " = ",save_param_val)
                cd.find('.'+xmlpath).text = save_param_val

def recurse_node2(root,xmlpath, cell_def_name):
    global save_param_val
    xmlpath = xmlpath + "//" + root.tag[root.tag.rfind('}')+1:]
    param_val = ''
    for child in root:
        if child.text == None:
            print(">>>> ", child, ".text is None")
            continue
        param_val = ' '.join(child.text.split())
        if param_val != '':
            # print('param value=',param_val, ' for ',end='')
            save_param_val = param_val
        recurse_node2(child,xmlpath,cell_def_name)
    if len(list(root)) == 0:
        # print(xmlpath)
        print(xmlpath,' = ',save_param_val)
        update_this_immune_cell_def_params(xmlpath, save_param_val, cell_def_name)
        save_param_val = None


#leaf_immune_cell_defs = ["CD8 Tcell", "macrophage", "neutrophil", "DC", "CD4 Tcell"]
for cd in xml_orig.findall('cell_definitions//cell_definition'):
    idx += 1
    if cd.attrib["name"] in leaf_immune_cell_defs:
        uep = cd
        print("\n---------------- processing ",cd.attrib["name"])   # 2  (0=default, 1=lung epi)
        # immune_uep = root.find('.//cell_definitions')
        for child in cd:
            print("------- calling recurse_node2 on child=",child)
            recurse_node2(child,"",cd.attrib["name"])

print("\nDone.")

#new_xml_file = "new_flat_config3.xml"
new_xml_file = "flat.xml"
tree_flat.write(new_xml_file)

with open(new_xml_file, 'r+') as f:
    new_xml = f.read()
    f.seek(0, 0)
    f.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n' + new_xml)

print("---> wrote ",new_xml_file, "(copy it to PhysiCell_settings.xml if desirable)\n")