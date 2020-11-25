# This script uses the 32 extra abbreviations that are set up as "@-strings" (page 40 of DM4) in I6 (@00 to @32)

# use the extra abbreviations spat by abbreviations.py
extra_abbrev = ["not", "est", "few ", "ind", "en ", "north", "wood", ", a", "generator", "cliff", ". A", "fence", "under", "round", "is ", " co", "ent", "ear", " anyth", "ever", " do", "...", "elevator", " st", "ake", " wh", "wards", "s. ", "ast", "way", "ock", "ill"]

if (len(extra_abbrev) >32):
    print("Error: too many extra abbreviations")
    exit

# Open the game source
f = open("tristam.inf", "r")
lines = f.readlines()
# Open somewhere to copy
g = open("tristam-crunch.inf", "w")

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
