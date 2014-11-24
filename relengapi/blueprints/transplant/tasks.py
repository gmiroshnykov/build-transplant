# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from flask import current_app
from relengapi.lib import celery
import actions
from repository import MercurialException

@celery.task
def add(x, y):
    return x + y

@celery.task()
def transplant(src, dst, items):
    try:
        return actions.transplant(src, dst, items)
    except MercurialException, e:
        return {
            'error': e.stderr
        }
