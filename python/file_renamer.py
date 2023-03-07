#!/usr/bin/env python3

import sys, os, re
from datetime import datetime

# strings to remove
stringstodelete = [ "unwanted_string1", "unwanted_string2" ]
# chars to replace by a whitespace
replacebywhitespace = [ ".", "_", "(", ")", "[", "]" ]

logfile = "rename.log"
f = open(logfile, "a", encoding="utf-8")

for i in range(1, len(sys.argv)):
    if not os.path.isfile(sys.argv[i]):
        print("%s is not a file" % sys.argv[i])
        continue
    filename = sys.argv[i]
    try:
        [newfilename, fileext] = os.path.splitext(os.path.basename(filename))
        # remove unwanted words
        for str in stringstodelete:
            newfilename = newfilename.replace(str, "")
        # replace special characters by whitespaces
        for str in replacebywhitespace:
            newfilename = newfilename.replace(str, " ")
        # replace non-ascii characters and leading/trailing whitespaces
        newfilename = "".join(c for c in newfilename if ord(c) < 128).strip()
        # put year in brackets (if at the end)
        newfilename = re.sub(r'([0-9]{4})$', r'(\1)', newfilename)
        # merge multiple whitespaces
        newfilename = ' '.join(newfilename.split())
        f.write("%s  file '%s' renamed to '%s%s'\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), os.path.basename(filename), newfilename, fileext.lower()))
        os.rename(filename, "%s/%s%s" % (os.path.dirname(filename), newfilename, fileext.lower()))
    except Exception as e:
        f.write("%s  an error occurred: %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e))

f.close()
