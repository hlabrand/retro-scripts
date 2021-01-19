# This script uses the 32 extra abbreviations that are set up as "@-strings" (page 40 of DM4) in I6 (@00 to @32)

# use the extra abbreviations spat by abbreviations.py
extra_abbrev = ["not", "est", "ind", "few ", " from", "en ", "north", "wood", "generator", "is ", "fence", "under", "round", "cliff", "ent", "ear", "elevator", " any", "ever", " do", " co", "wards", "ake", ".^", " st", "Tristam Isl", "ock", "ast", "ill", " what", "way", "manage"]

if (len(extra_abbrev) >32):
    print("Error: too many extra abbreviations")
    exit
    
    
import optparse
popt = optparse.OptionParser(usage='extra-abbrev.py FILENAME')
(opts, args) = popt.parse_args()
if (not args):
    popt.print_help()
    exit(-1)
filename = None
if (args):
    filename = args.pop(0)

radical = filename.split(".")[0]
print(radical)

# Open the game source
f = open(radical+".inf", "r")
lines = f.readlines()
# Open somewhere to copy
g = open(radical+"-crunch.inf", "w")

flag = 0
for i in range(0,len(lines)):
    l = lines[i]
    # we need to skip the abbreviations themselves - this is disallowed by the standards, and some interpreters (e.g. Bocfel) will crash
    if (l.find("Abbreviate") == -1):
        # is the flag up? if so, time to write the string statements
        if (flag == 1):
            for j in range(0, len(extra_abbrev)):
                g.write("string "+str(j)+" \""+extra_abbrev[j]+"\";\n")
        flag = 0
        # detect initialise
        if (l[0:12] == "[ Initialise" or l[0:11] == "[Initialise"):
            flag=1
        # actually replace the string
        for j in range(0, len(extra_abbrev)):
            new_line = ""
            if (l.count(extra_abbrev[j])):
                # we're interested
                st = "@"
                if (j < 10):
                    st += "0"
                st += str(j)
                # but we don't want to replace inside the dictionary, only in strings
                # assume a string isn't running on several lines, that it was just open on the same line
                string_begun = 0
                len_abb = len(extra_abbrev[j])
                k=0
                while (k < len(l)):
                    if (k < len(l)-len_abb and l[k:k+len_abb] == extra_abbrev[j] and string_begun == 1):
                        new_line += st
                        k += len_abb
                    else:
                        if (l[k] == "\""):
                            string_begun = 1-string_begun
                        new_line += str(l[k])
                        k += 1
                l = new_line
    g.write(l)
    
f.close()
g.close()
