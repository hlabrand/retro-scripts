###########################
# Z3 to ZEMU
# A small script to convert a z3 file into the format expected by the
#    ZEMU interpreter for TI-84+ CE
# Written by Hugo Labrande
# With assistance from Nicholas Hunter Mosier

myfile_name = "tristam.z3"

# ZEMU defaults
ZEMU_PAGE_SIZE = 4096
FLAG = 1

# determine the prefix
prefix = myfile_name[0:4].upper()
#print("Prefix : "+prefix)

# determine the number of page files (better for performance)
import os
myfile_size = os.stat(myfile_name).st_size
#print(myfile_size)
nb_pages = myfile_size // 4096 + 1
#print("Number of pages : "+str(nb_pages))

# Start address of the static memory
#    according to the z-machine spec, this is 2 bytes starting at 0xe of the z-machine
f = open(myfile_name, "rb")
f.read(14)
a = f.read(1)
b = f.read(1)
f.close()
start_address_static_memory = int.from_bytes(a, "big")*256 + int.from_bytes(b, "big")
#print(start_address_static_memory)

# list that will hold all the page names (needed for the main 8xv file)
list_variables = bytearray([])

# write the page files except the last one
myfile = open(myfile_name, "rb")
for i in range(1, nb_pages+1):
    # create the header prefix
    #   for format info see http://merthsoft.com/linkguide/ti83+/fformat.html
    # Signature
    signature = "**TI83F*"
    header_prefix = bytearray([ord(signature[i]) for i in range(0, 8)])
    # Further signature
    further_signature = bytearray([26, 10, 0])
    header_prefix += further_signature
    # Comment : 42 char
    #comment = "Created by z3tozemu.py"
    comment = "Created by tipack 0.1"
    comment_b = bytearray([ ord(comment[i]) for i in range(0, len(comment)) ])
    padding = bytearray([0 for i in range(len(comment), 42)])
    header_prefix += comment_b+padding
    # Length :
    #    always 4096 for zemu, except for the last page
    #    19 for the variable type info
    # Careful: 2-byte values are always little endian!
    if (i < nb_pages):
        page_size = ZEMU_PAGE_SIZE
    else:
        page_size = myfile_size % ZEMU_PAGE_SIZE # leftovers
    file_len = page_size+19
    header_prefix += bytearray([ file_len % 256, file_len // 256 ])
    # Info on the variable entry: first part
    data_header_part1 = bytearray([])
    # always 11 or 13
    data_header_part1 += bytearray([13 % 256, 13 // 256])
    # Length of variable data : page_size + 2 bytes for the checksum
    vardata_len = page_size+2
    #print(vardata_len)
    data_header_part1 += bytearray([vardata_len % 256, vardata_len // 256])
    # Variable type (program)
    data_header_part1 += bytearray([0x15])
    
    # Name of this variable
    page_name = prefix+"R"+chr(ord('a')+(i // 26))+chr(ord('a')-1+(i % 26))
    page_name_bytes = bytearray([ord(page_name.upper()[i]) for i in range(0,len(page_name))])
    #print(page_name)
    data_header_part2 = page_name_bytes
    data_header_part2 += bytearray([0]) # null termination character
    # add it to the list (has to be 12 char)
    if ( (i-1)*page_size < start_address_static_memory): # TODO: i have no idea why
        list_variables += page_name_bytes
        list_variables += bytearray([0, 0, 0, 0, 0, 0, FLAG])
    else:
        list_variables += page_name_bytes
        list_variables += bytearray([0, 0, 0, 0, 0, 0, 0,])
    
    # Info on the variable entry:
    # version (0x00), flag (0x00, non archived), len of data (see vardata_len)
    data_header_part2 += bytearray([0,0])
    data_header_part2 += bytearray([vardata_len % 256, vardata_len // 256])
    # then the variable data
    # it's a program, so a y-variable: starts with indicating the len
    data_header_part2 = data_header_part2 + bytearray([page_size % 256, page_size // 256])
    # then the data itself
    data = myfile.read(page_size)
    # Write checksum
    sum = 0
    for i in range(0, len(data_header_part1)):
        sum += int(data_header_part1[i])
    for i in range(0, len(data_header_part2)):
        sum += int(data_header_part2[i])
    for i in range(0,page_size):
        sum += int(data[i])
    checksum = bytearray([sum % 256, (sum // 256)%256])
    #print(checksum)
    
    # write it
    f = open(page_name+".8xv", "wb")
    f.write(header_prefix)
    f.write(data_header_part1)
    f.write(data_header_part2)
    f.write(data)
    f.write(checksum)
    f.close()

# Write the list of variables 

# create the header prefix
#   for format info see http://merthsoft.com/linkguide/ti83+/fformat.html
# Signature
signature = "**TI83F*"
header = bytearray([ord(signature[i]) for i in range(0, 8)])
# Further signature
further_signature = bytearray([26, 10, 0])
header += further_signature
# Comment : 42 char
#comment = "Created by z3tozemu.py"
comment = "Created by tipack 0.1"
comment_b = bytearray([ ord(comment[i]) for i in range(0, len(comment)) ])
padding = bytearray([0 for i in range(len(comment), 42)])
header += comment_b+padding
# Length :
#    from experimenting, needs to be length of program + 27
len1 = len(list_variables) + 27
#print(len1)
header += bytearray([ len1 % 256, len1 // 256 ])
# Info on the variable entry: first part
data_header = bytearray([])
# always 11 or 13
data_header += bytearray([13 % 256, 13 // 256])
# Length of the rest of the file :
#   len of the list + 8 bytes for the flags/bytes/etc string + 2 bytes for the checksum
vardata_len = len(list_variables) +8+2
#print(vardata_len)
data_header += bytearray([vardata_len % 256, vardata_len // 256])
# Variable type (program)
data_header += bytearray([0x15])
# Name of the file = prefix
data_header += bytearray([ord(prefix[i]) for i in range(0,4)])
data_header += bytearray([0 for i in range(len(prefix), 8)])
# Version (0x00), flag (0x00), len (see vardata_len)
data_header += bytearray([0, 0, vardata_len % 256, vardata_len // 256])
# len of the variable data : vardata_len - 2 (the checksum isnt part of it)
data_header += bytearray([(vardata_len - 2) % 256, (vardata_len-2) // 256])
# pagemask byte
data_header += bytearray([ 4096 // 256 - 1])
# pagebits byte : "hamming weight of 4096-1" minus 8 (because high bits)
data_header += bytearray([12-8])
# len of the story file
data_header += bytearray([ myfile_size % 256, (myfile_size // 256) % 256, (myfile_size // 65536) % 256 ])
# number of pages
data_header += bytearray([nb_pages])
# Start address of static Z-memory
data_header += bytearray([start_address_static_memory % 256, start_address_static_memory // 256])

# Checksum
sum = 0
for i in range(0, len(data_header)):
    sum += int(data_header[i])
for i in range(0,len(list_variables)):
    sum += int(list_variables[i])
checksum = bytearray([sum % 256, (sum // 256)%256])
#print([sum % 256, (sum // 256)%256])

# Write in file
f = open(prefix.upper()+".8xv", "wb")
f.write(header)
f.write(data_header)
f.write(list_variables)
f.write(checksum)
f.close()