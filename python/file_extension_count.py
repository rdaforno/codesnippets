import os, sys

if len(sys.argv) < 2:
    sys.exit()
    
print("analyzing " + sys.argv[1] + "...")

extensiondict = {}
for root, dirs, files in os.walk(sys.argv[1]):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext not in extensiondict:
            extensiondict[ext] = 1
        else:
            extensiondict[ext] = extensiondict[ext] + 1

for key in extensiondict:
    print(key + "\t" + str(extensiondict[key]))

input("Press any key to exit...")