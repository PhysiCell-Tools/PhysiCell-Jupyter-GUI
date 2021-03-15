# flatten_cell_def_xml.py - convert a PhysiCell_settings.xml with inheritance of <cell_definitions>
#                      into one without inheritance, i.e., verbose leaf <cell_definition>s.
#
#
# Author: Randy Heiland
#

import xml.etree.ElementTree as ET
import sys
import string

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
print("\n--- Phase 0: Build a Python dict, cell_def, that contains keys = name and values = {'ID':value, 'parent':value}" )

tree = ET.parse(xml_file)  
xml_root = tree.getroot()

# "cell_def" will be a dict with key = cell_def name, value = {'ID':value, 'parent':value}
cell_def = {}
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
    cell_def[cd.attrib['name']] = attrib_dict

    # if (cell_def.attrib['name'] != 'default') and ('parent_type' in cell_def.attrib.keys() ): # and ('immune' in cell_def.attrib['parent_type'] ) :
#    if (cell_def.attrib['name'] != 'default') and (cell_def.attrib['name'] != 'immune') and ('parent_type' in cell_def.attrib.keys() ): # and ('immune' in cell_def.attrib['parent_type'] ) :
#        leaf_cell_defs[cell_def.attrib['name']] = cell_def.attrib['ID']
        
#print('leaf_cell_defs= ',leaf_cell_defs)  
print('cell_def= ',cell_def)  

#leaf_immune_cell_defs = ["CD8 Tcell", "macrophage", "neutrophil", "DC", "CD4 Tcell", "fibroblasts"]
# leaf_immune_cell_defs = list(leaf_cell_defs.keys())
# leaf_immune_cell_defs.remove('lung epithelium')
# print('leaf_immune_cell_defs= ',leaf_immune_cell_defs)  

xml_root = tree.getroot()
#--------------------------------------------------
print("\n--- Phase 1: create a new .xml containing N copies of 'default' cell_definition, with desired names.")

#tree0 = tree
#flat_root = xml_root
# default_cell_def = xml_root.find("cell_definitions//cell_definition[@name='default']")
cell_defs = tree.find('cell_definitions')
# root_node = cell_defs.getroot()
#--------------------------------------------------
print("--- Remove all but root node (top cell_def)")
# May NOT be called "default", e.g.
# cancer_biorobots:         <cell_definition name="cancer cell" ID="0">
# Assuming root node is the first one.
root_node = True
for cd in list(cell_defs):
    # print(cell_def.tag, cell_def.attrib['name'])
    if (root_node):
        root_node = False
    else:
        print("removing ", cd.attrib['name'])
        cell_defs.remove(cd)
        # ET.SubElement(root_node,default_cell_def)
        # cell_defs.insert(0,default_cell_def)

# new_xml_file = "new_flat_config1.xml"
# new_xml_file = "flat.xml"
# tree.write(new_xml_file)
#sys.exit()

#--------------------------------------------------
# tree = ET.parse("new_flat_config1.xml")  
# xml_root = tree.getroot()
# For each child of the root node, make a copy of the root.

#default_cell_def = xml_root.find("cell_definitions//cell_definition[@name='default']")
# NB: Assume the root will be the first one
root_cell_def = xml_root.find("cell_definitions//cell_definition")
root_name = root_cell_def.attrib['name'] 
print("--- Insert duplicate root cell_def for of its children")
print("   root_name = ",root_name)
cd_vals = list(cell_def.values())

for cd in cd_vals:
    # print('-- ',leaf)
#    print(cell_def.tag, cell_def.attrib['name'])
    # print("insert default for ", leaf.attrib['name'])
    # print("insert default for ", leaf)
    # default_cell_def.attrib['name'] = leaf
    # tmp_cd.attrib['name'] = leaf
    # cell_defs.insert(0,default_cell_def)

    # cell_defs.insert(0,default_cell_def)
    if cd['parent'] == root_name:
        print('inserting child of ',root_name)
        cell_defs.insert(0,root_cell_def)
        # root_cell_def.attrib['name'] = 'bar'
        # child = xml_root.find("cell_definitions//cell_definition[2]")
        # child.attrib['name'] = 'foo'
#sys.exit()

# NB! Need to save the file at this point and read it back in to continue processing.
new_xml_file = "tmp1.xml"
tree.write(new_xml_file)

#--------------------------------------------
tree = ET.parse("tmp1.xml")  
xml_root = tree.getroot()
idx = 1
cd_keys = list(cell_def.keys())
for cd in cd_vals:
    if cd['parent'] == root_name:
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
#--------------------------------------------------
#leaf_immune_cell_defs = ["CD8 Tcell", "macrophage", "neutrophil", "DC", "CD4 Tcell","fibroblasts"]
# leaf_immune_cell_defs = ["CD8 Tcell"]
def update_all_immune_cell_def_params(xmlpath, save_param_val, substrate_name_in):
    print("*** ENTER: update_all_substrate_params: substrate_name_in (param) = ",substrate_name_in)
    for cell_def in leaf_immune_cell_defs:
        print("  * cell_def = ",cell_defs)
        for cd in xml_flat_root.findall('cell_definitions//cell_definition'):  # find *this* cell_def in flattened XML
            if cd.attrib['name'] == cell_def:  # we've found one of the immune cell types (clone of "default")
                print('  -- update ',cell_def, ', xmlpath=',xmlpath, " = ",save_param_val)
                if "secretion//substrate" in xmlpath:   # need to handle secretion substrate carefully; match name 
                    print("  =======  need special handling of secretion//substrate  for substrate_name_in=", substrate_name_in)

                    #---------
                    uep_secretion = cd.find('.//phenotype//secretion')  # get the <secretion> element
                    print("  =======  uep_secretion=", uep_secretion)
                    for elm_sub in uep_secretion.findall('substrate'):  # for each <substrate name=...> in <secretion>
                        substrate_name = elm_sub.attrib["name"]
                        print('  *-- elm_sub ',elm_sub, ", name=",substrate_name)
                        if (substrate_name_in != substrate_name):
                            print("   THIS IS NOT THE DROID YOU'RE LOOKING FOR")
                            continue
                        print('   -- update ',uep_secretion, ', xmlpath=',xmlpath, ", save_param_val=",save_param_val)
                        # if "secretion//substrate" in xmlpath:
                        if "substrate//uptake_rate" in xmlpath:
                            print("   =======  need special handling of secretion//substrate//uptake_rate  for ", substrate_name_in)
                            if "uptake_rate" in xmlpath[-13:]:
                                print("\n   =======     handle uptake_rate")
                                print("   =======     xmlpath[:-13]",xmlpath[:-13] )
                                print("   =======     substrate_name as param= ",substrate_name_in )
                                if (substrate_name == substrate_name_in):
                                    print("   WEEEEEEEEEEEEE!!! match found")
                                    print('   xmlpath=',xmlpath)
                                    # elm.find('.'+xmlpath).text = save_param_val   # FINALLY, update the value
                                    # elm_sub.find('.'+xmlpath).text = save_param_val   # FINALLY, update the value
                                    elm_sub.find('.'+'//uptake_rate').text = save_param_val   # FINALLY, update the value
                                    break

                    #---------
                elif "death//model" in xmlpath:   
                    print("=================   process <death>   =================")
                    uep_death = cd.find('.//phenotype//death')  # get the <death> element; match <model name=...>
                    for elm_sub in uep_death.findall('model'):  
                        print("   >>> found death model = ",elm_sub.attrib["name"])
                    print("=================   end <death>  (sounds good to me)  =================")

                    # if "uptake_rate" in xmlpath[-13:]:
                    #     print("\n  =======     handle uptake_rate")
                    #     parent_elm = cd.find('.' + xmlpath[:-13])
                    #     print("  =======     xmlpath[:-13]",xmlpath[:-13] )
                    #     print("  =======     this substrate(parent) name= ",parent_elm.attrib["name"] )
                    #     print("  =======     substrate_name_in = ",substrate_name_in )
                    #     if (substrate_name_in == parent_elm.attrib["name"]):
                    #         print(" WEEEEEEEEEEEEE!!! match found")
                    #         # elm_sub.find('.'+'//uptake_rate').text = save_param_val   # FINALLY, update the value
                    #         cd.find('.'+xmlpath).text = save_param_val
                    #         break
                    # parent_elm = cd.find('.' + xmlpath[:-13])
                    # # print('  -- parent ',parent_elm)
                    # if (parent_elm.tag == 'substrate'):
                    #     print('  -- parent is ',parent_elm.tag, parent_elm.attrib["name"])
                    # print("   parent=", cd.find('.'+xmlpath).getparent() )
                # cd.find('.'+xmlpath).text = save_param_val
                # cd.'.//cell_definition[1]//phenotype//mechanics//cell_cell_adhesion_strength').text = save_param_val
    print("*** EXIT ")

def recurse_node(root,xmlpath,substrate_name):
    global save_param_val
    xmlpath = xmlpath + "//" + root.tag[root.tag.rfind('}')+1:]
    param_val = ''
    # substrate_name = ""
    if (root.tag == "substrate") and (len(root.attrib) > 0):   # don't want substrate for chemotaxis, just secretion
        print("recurse_node: ========>> found substrate (for secretion), attrib=",root.attrib)
        substrate_name = root.attrib["name"]
        print("recurse_node: ========>> substrate_name =",substrate_name ,"\n")
    for child in root:
        param_val = ' '.join(child.text.split())
        if param_val != '':
            # print('param value=',param_val, ' for ',end='')
            save_param_val = param_val
            # uep.find('.//cell_definition[1]//phenotype//mechanics//cell_cell_adhesion_strength').text = str(self.float27.value)
        recurse_node(child,xmlpath,substrate_name)
    if len(list(root)) == 0:  # we are finally at the bottom of the recursion; the element of interest.
        # e.g.  //phenotype//motility//options//chemotaxis//direction  =  1
        #       //phenotype//secretion//substrate//uptake_rate  =  0.01    (WRONG - also need to know substrate *name*)
        # print(xmlpath)
        print(xmlpath,' = ',save_param_val)
        update_all_immune_cell_def_params(xmlpath, save_param_val, substrate_name)


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