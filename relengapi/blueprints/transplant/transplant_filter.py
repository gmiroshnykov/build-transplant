#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
