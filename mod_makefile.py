import platform

with open("src/Makefile") as infile:
    with open("Make2","w") as outfile:
        for line in infile:
            sline = line.split()
            if len(sline) > 0:
                if sline[0] == "PROGRAM_NAME":
                    # print('got PROGRAM_NAME')
                    newline = sline[0] + sline[1] + " myproj\n"
                    outfile.write(newline)
#                    outfile.write("\nUNAME := $(shell uname)\n")
                elif sline[0] == "clean:":
                    # print('got ',sline[0])
#                    outfile.write(line)
                    nanohub_targets = "# next 2 targets for nanoHUB\ninstall: all\n\tcp $(PROGRAM_NAME) ../bin\n\ndistclean: clean\n\trm -f ../bin/$(PROGRAM_NAME)\n\n"
                    outfile.write(nanohub_targets)
                    outfile.write("clean:\n")
                elif "rm -f $(PROGRAM_NAME)*" in line:
#                    outfile.write("\tifeq ($(OS),Windows_NT)\n")
#                    outfile.write("\t\trm -f $(PROGRAM_NAME)*\n")
#                    outfile.write("\telse\n")
#                    outfile.write("\t\trm -f $(PROGRAM_NAME)\n")
                    outfile.write("\trm -f $(PROGRAM_NAME)\n")
#        
#clean:
#        rm -f *.o
#        rm -f $(PROGRAM_NAME)
#                elif "clean" in sline[0]:
#                    print('got ',sline[0])
                else:
                    outfile.write(line)
            else:
                outfile.write(line)
