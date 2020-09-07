###########################
# testSupercart.py : does my game require a supercart or not?

name = "tris.z3"
f = open(name, "rb")
f.read(4)
a = f.read(1)
b = f.read(1)
f.close()
start_high_memory = int.from_bytes(a, "big")*256 + int.from_bytes(b, "big")
#print(start_high_memory)

if (start_high_memory > 22528):
    print("======================================================")
    print("Warning!! This game requires a SuperCart !")
    print("======================================================")
else:
    print("This game doesn't require a SuperCart.")
