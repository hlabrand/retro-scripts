# note: there is a bug because it doesn't always correspond to what the inform compiler says, thus yielding abbreviations that aren't the best; find out why (because inform abbreviates in a different order than what you give it?)

# gametext.txt ends with a printout of the dictionary, but the dictionary is not abbreviated
# so you want to count frequencies for all the file except the "last few lines"
# tweak this constant to get better estimates
FIRST_FEW_LINES = 70  # always skip the first 70 lines : 6 lines of header and 64 of your own abbreviations
LAST_FEW_LINES = 100

# disregard abbreviations that don't save enough bytes
MIN_SCORE = 20


f = open("gametext.txt", "r")
lines = f.readlines()
lines = lines[FIRST_FEW_LINES:len(lines)-LAST_FEW_LINES]

# keep an updated version of the abbreviated text
wholetext = ""
for i in range(0,len(lines)):
    wholetext += lines[i] + "\n"

dic = {}

# From experience, I've never found abbreviations of 10 letters that helped
MAX_LEN = 9

for n in range(3,MAX_LEN+1):
    # each step takes around 1 second on my computer
    print("   Counting frequencies... ("+str(n)+"/"+str(MAX_LEN)+")")
    for li in lines:
        for i in range(0, len(li)-n):
            s = li[i:i+n]
            if (s in dic.keys()):
                dic[s] = dic[s] + 1
            else:
                dic[s] = 1
                    
## use the same formula as inform :
##     2*((abbrev_freqs[i]-1)*abbrev_quality[i])/3 with abbrev_quality = len -2
l = []
for p in dic.items():
    score = int(2*((p[1]-1)*(len(p[0])-2))/3)
    ## Only add things that save enough bytes (to speed up the search)
    if (score > MIN_SCORE):
        l += [[p[0], score ]]

# find the first abbreviation

abbr = []
print("Determining abbreviation "+str(len(abbr)+1)+"...")
l = sorted(l, key=lambda x: x[1])
steps = 0
while (len(abbr) < 64 or len(l) > 0):
    steps += 1
    # potential winner
    winner = l[len(l)-1]
    print("Trying "+str(winner[0])+"...")
    # let's confirm the score
    actual_freq = wholetext.count(winner[0])
    actual_score = int(2*((actual_freq-1)*(len(winner[0])-2))/3)
    print ("Let's compare to the score of "+str(l[len(l)-2][0])+", which is", str(l[len(l)-2][1]))
    if (actual_score >= l[len(l)-2][1]):
        print("Found string : '"+str(winner[0])+"' (saves "+str(actual_score)+" bytes)")
        # the revised score is still better than the next in line's
        abbr = abbr + [str(winner[0])]
        print("Determining abbreviation "+str(len(abbr)+1)+"...")
        # update the text
        wholetext = wholetext.replace(str(winner[0]), "$")
        # update the array
        lcopy = []
        for i in range(0, len(l)-1): # skip the last one since it's the abbrev
            # only add to the copy the strings not containing the abbreviated string
            if (str(winner[0]) not in str(l[i][0])):
                lcopy += [l[i]]
        l = lcopy
        print ("Array updated; now has"+str(len(l))+" entries")
        # no need to sort; the order of the score hasn't been changed
    else: # calculating the actual score knocked that back a few pegs; sort again
        l[len(l)-1][1] = actual_score
        #print("Changed the score of "+str(l[len(l)-1][0])+" to "+str(actual_score))
        #print("Sorting again...")
        l = sorted(l, key=lambda x: x[1])
        
    
    
            
print("Found 64 abbreviations in"+str(steps)+"steps")

s = "Abbreviate "
for i in range(0,64):
    s = s + '"' + abbr[i] +'" '
s += ";"
print(s)

f.close()
