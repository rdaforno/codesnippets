#!/usr/bin/env python3

import sys, os
from datetime import datetime

# strings to remove
stringstodelete = [ "unwanted_string1", "unwanted_string2" ]
# chars to replace by a whitespace
replacebywhitespace = [ ".", "_", "(", ")" ]

logfile = "rename.log"

for i in range(1, len(sys.argv)):
    if not os.path.isfile(sys.argv[i]):
        print("%s is not a file" % sys.argv[i])
        continue
    filename = sys.argv[i]
    try:
        [newfilename, fileext] = os.path.splitext(os.path.basename(filename))
        for str in stringstodelete:
            newfilename = newfilename.replace(str, "")
        for str in replacebywhitespace:
            newfilename = newfilename.replace(str, " ")
        # replace non-ascii characters
        newfilename = "".join(c for c in newfilename if ord(c) < 128)
        # merge multiple whitespaces
        newfilename = ' '.join(newfilename.split())
        f.write("%s  file '%s' renamed to '%s%s'\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(filename), newfilename, fileext.lower()))
        os.rename(filename, "%s/%s%s" % (os.path.dirname(filename), newfilename, fileext.lower()))
    except Exception as e:
        f.write("%s  an error occurred: %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e))

f.close()
