#!/usr/bin/env python
import os
import sys

if len(sys.argv) < 2:
    print "ERROR: no message file"
    exit(1)

if 'TRANSPLANT_MESSAGE' not in os.environ:
    print "ERROR: TRANSPLANT_MESSAGE not set"
    exit(1)

MESSAGE_FILE = sys.argv[1]

output = None
with open(MESSAGE_FILE, 'r+') as f:
    lines = f.readlines()
    output = [line for line in lines if line.startswith('#')]
    output.append(os.environ['TRANSPLANT_MESSAGE'])

    f.seek(0)
    f.writelines(output)
    f.truncate()

exit(0)
