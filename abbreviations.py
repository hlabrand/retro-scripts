#   abbreviations.py
#      by Hugo Labrande
#      Licence: public domain
#   Version: 09-Dec-2020

# This script finds great abbreviations for your Inform game, which helps when space is tight.
# It finds up to 20% more savings than Inform's "-u" switch ; this is about 4k on a 128k story file.
# As a bonus, it's just as fast as that switch when you look at abbreviations of length between 2 and 9.

# Abbreviation strings still aren't an exact science!
#   Due to the fact that the number of 5-bit units has to be a multiple of 3 (and as such gets padded), we can only give estimates


# Input: gametext.txt file containing all the text in your game
#    (for instance use the -f flag of the Inform 6 compiler, or a command like
#                cat *.zap | grep -o '".*"' | sed 's/"\(.*\)"/\1/g' >gametext.txt
#     for ZILF/ZILCH - don't forget to exclude the dictionary words though.)

# Output: the first 64 abbreviations, in Inform's format; the extra abbreviations, in a Python-style list (to use with my extra-abbrev.py)
#         If you specify the -z flag, a file "mygame_freq.zap" will be created in the correct format, ready to use with ZILF/ZILCH.


# In I6, gametext.txt ends with a printout of the dictionary, but the dictionary is never abbreviated
# so you want to count frequencies for all the file except the "last few lines"
# tweak this constant to get better estimates
FIRST_FEW_LINES = 0  # With I6, always skip the first 70 lines : 6 lines of header and 64 of your own abbreviations
LAST_FEW_LINES = 705

# disregard abbreviations that don't save enough units
MIN_SCORE = 20

# How many do you want?
#NUMBER_ABBR = 64
NUMBER_ABBR = 96   # if you want an extra small file, use "string 14 XXXX" (page 40 of the DM4)

# One-char strings can be 4 unit longs (for instance ";"), so you could save 2 units per occurence; however at the date of writing, Inform refuses to abbreviate strings of length 0 or 1...
# So starting at 2 is a good idea for now
MIN_LEN = 2
MAX_LEN = 60



ZAP_OUTPUT = 0
import sys, getopt

# Deal with command-line arguments
# TODO allow the specification of the name of the file, the lines, etc - I'm being lazy for now
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv,"z",)
except getopt.GetoptError:
    print ('Usage: python3 abbreviations.py [-z]')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-z':
        ZAP_OUTPUT = 1


f = open("gametext.txt", "r")
lines = f.readlines()
lines = lines[FIRST_FEW_LINES:len(lines)-LAST_FEW_LINES]

# keep an updated version of the abbreviated text
wholetext = ""
for i in range(0,len(lines)):
    wholetext += lines[i] + "\n"


l = []
        

for n in range(MIN_LEN,MAX_LEN+1):
    dic = {}
    # each step takes around 1 second on my computer
    print("   Counting frequencies... ("+str(n)+"/"+str(MAX_LEN)+")")
    for li in lines:
        for i in range(0, len(li)-n):
            s = li[i:i+n]
            if (s in dic.keys()):
                dic[s] = dic[s] + 1
            else:
                dic[s] = 1
                    
    ## If you want to use the same formula as inform :
    ##     2*((abbrev_freqs[i]-1)*abbrev_quality[i])/3 with abbrev_quality = len -2
    ## A better one is actually counting the units.

    for p in dic.items():
        i = 0
        units = 0
        wd = p[0]
        while (i < len(wd)):
            letter = wd[i]
            if (ord(letter) == 32):
                units += 1 ## space = char 0
            elif (ord(letter) >= 97 and ord(letter) <= 122):
                units += 1 ## A0 alphabet
            elif (ord(letter) >= 65 and ord(letter) <= 90):
                units += 2 ## A1 alphabet
            elif (letter in "^0123456789.,!?_#'~/\-:()"):
                units += 2 ## A2 alphabet
            else:
                if (letter == '@'):
                    ## most likely an accented character like @:e : skip the next 2 letters
                    i+=2
                units += 4 
            i += 1
        ## number of occurences (-1 since you have to write the abbr somewhere) * units saved (units/2) = total units saved
        ## we compute the number of units saved
        ## score = int ((p[1]-1)* (units-2)/3 * 2)
        score = (p[1]-1)* (units-2)
        ## Only add things that save enough units (to speed up the search)
        ## Add something to say when we last updated the score
        if (score > MIN_SCORE):
            l += [[p[0], score, units, 0 ]]

# find the first abbreviation

abbr = []
print("Determining abbreviation "+str(len(abbr)+1)+"...")
l = sorted(l, key=lambda x: x[1])

if ZAP_OUTPUT == 1:
    g = open("mygame_freq.zap", "w")

final_savings = 0

# Python's count thinks "****" has 3 "**", when it only replaces twice; this makes a big difference
def my_count(text, st):
    c = 0
    i = 0
    while (i <= len(text)-len(st)):
        # if they have the same first letter...
        if (text[i] == st[0]):
            # if it's a match
            if (text[i:i+len(st)] == st):
                # increase the count and SKIP TILL THE END OF THE MATCH
                c += 1
                i += len(st)
            else:
                i +=1
        else:
            i+=1
    return c
    

steps = 0
while (len(abbr) < NUMBER_ABBR and len(l) > 0):
    steps += 1
    # determine the leaders
    leading_score = l[len(l)-1][1]
    n=1
    while( l[len(l)-1-n][1] == leading_score ):
        n += 1
    print("Found "+str(n)+" leaders with score "+str(leading_score))
    # see if they all have updated score
    flag = 1
    for i in range(1, n+1):
        if (l[len(l)-i][3] != len(abbr)):
            l[len(l)-i][3] = len(abbr)
            actual_freq = my_count(wholetext, l[len(l)-i][0])
                #actual_score = int(2*(actual_freq-1)*(l[len(l)-i][2]-2)/3)
            actual_score = (actual_freq-1)*(l[len(l)-i][2]-2)
            l[len(l)-i][1] = actual_score
            flag = 0
    if ( flag == 0 ):
        l = sorted(l, key=lambda x: x[1])
        print("The leaders weren't what we thought; let's sort again...")
    else:
        # at this point, we have a few candidates with equal actual score
        # Matthew Russotto's idea for a tiebreaker: take the high frequency
        #    one (meaning the one with the most weight)
        max = 1
        for i in range(2, n+1):
            if (l[len(l)-max][2] < l[len(l)-i][2]):
                max = i
        # we found our abbreviation
        winner = l[len(l)-max]
        actual_freq = my_count(wholetext, winner[0])
        print("Found string : '"+str(winner[0])+"' (saves "+str(winner[1])+" units)")
        final_savings += winner[1]
        if ZAP_OUTPUT == 1:
            g.write("        .FSTR FSTR?"+str(len(abbr)+1)+",\""+str(winner[0])+"\"        ; "+str(actual_freq)+"x, saved "+str((actual_freq-1)*(winner[2]-2))+"\n")
        # the revised score is still better than the next in line's
        abbr = abbr + [str(winner[0])]
        print("Determining abbreviation "+str(len(abbr)+1)+"...")
        # update the text
        wholetext = wholetext.replace(str(winner[0]), "$")
        # update the array
        lcopy = []
        for i in range(0, len(l)):
            # only add to the copy the strings not containing the abbreviated string
            if (str(winner[0]) not in str(l[i][0])):
                lcopy += [l[i]]
        l = lcopy
        print ("Array updated; now has"+str(len(l))+" entries")
        # no need to sort; the order of the score hasn't been changed
        
        
if ZAP_OUTPUT == 1:
    endoffile="WORDS::\n        FSTR?1\n        FSTR?2\n        FSTR?3\n        FSTR?4\n        FSTR?5\n        FSTR?6\n        FSTR?7\n        FSTR?8\n        FSTR?9\n        FSTR?10\n        FSTR?11\n        FSTR?12\n        FSTR?13\n        FSTR?14\n        FSTR?15\n        FSTR?16\n        FSTR?17\n        FSTR?18\n        FSTR?19\n        FSTR?20\n        FSTR?21\n        FSTR?22\n        FSTR?23\n        FSTR?24\n        FSTR?25\n        FSTR?26\n        FSTR?27\n        FSTR?28\n        FSTR?29\n        FSTR?30\n        FSTR?31\n        FSTR?32\n        FSTR?33\n        FSTR?34\n        FSTR?35\n        FSTR?36\n        FSTR?37\n        FSTR?38\n        FSTR?39\n        FSTR?40\n        FSTR?41\n        FSTR?42\n        FSTR?43\n        FSTR?44\n        FSTR?45\n        FSTR?46\n        FSTR?47\n        FSTR?48\n        FSTR?49\n        FSTR?50\n        FSTR?51\n        FSTR?52\n        FSTR?53\n        FSTR?54\n        FSTR?55\n        FSTR?56\n        FSTR?57\n        FSTR?58\n        FSTR?59\n        FSTR?60\n        FSTR?61\n        FSTR?62\n        FSTR?63\n        FSTR?64\n        FSTR?65\n        FSTR?66\n        FSTR?67\n        FSTR?68\n        FSTR?69\n        FSTR?70\n        FSTR?71\n        FSTR?72\n        FSTR?73\n        FSTR?74\n        FSTR?75\n        FSTR?76\n        FSTR?77\n        FSTR?78\n        FSTR?79\n        FSTR?80\n        FSTR?81\n        FSTR?82\n        FSTR?83\n        FSTR?84\n        FSTR?85\n        FSTR?86\n        FSTR?87\n        FSTR?88\n        FSTR?89\n        FSTR?90\n        FSTR?91\n        FSTR?92\n        FSTR?93\n        FSTR?94\n        FSTR?95\n        FSTR?96\n\n        .ENDI"
    g.write(endoffile)
    g.close()
            
print("Found "+str(NUMBER_ABBR)+" abbreviations in"+str(steps)+"steps; they saved "+str(final_savings)+" units (~"+str(2*int(final_savings/3))+" bytes)")

s = "Abbreviate "
for i in range(0,64):
    s = s + '"' + abbr[i] +'" '
s += ";"
print(s)

if (NUMBER_ABBR > 64):
    s = "Extra abbreviations : [";
    for i in range(64, NUMBER_ABBR):
        s = s + '"' + abbr[i] +'", '
s = s[0:len(s)-2] # remove trailing comma
s += "]"
print(s)

f.close()
