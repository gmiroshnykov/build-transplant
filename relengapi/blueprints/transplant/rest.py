# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import wsme.types

class CommitInfo(wsme.types.Base):

    """Repository commit info."""

    node = unicode
    date = unicode
    author = unicode
    author_email = unicode
    message = unicode


class RevsetInfo(wsme.types.Base):

    """Repository revision set info."""

    commits = wsme.types.wsattr([CommitInfo], mandatory=True)


class TransplantItem(wsme.types.Base):

    """An item (commit or revset) to transplant."""

    #: commit to transplant (as is)
    commit = unicode

    #: revset to transplant (squashed)
    revset = unicode

    #: transplanted commit message
    message = unicode


class TransplantTask(wsme.types.Base):

    """Transplant task."""

    _name = "TransplantTask"

    #: source repository
    src = wsme.types.wsattr(unicode, mandatory=True)

    #: destination repository
    dst = wsme.types.wsattr(unicode, mandatory=True)

    #: items to transplant
    items = wsme.types.wsattr([TransplantItem], mandatory=True)


class TransplantTaskAsyncResult(wsme.types.Base):

    """ Transplant task async result."""

    #: task id
    task = unicode

    #: error
    error = unicode

class TransplantTaskResult(wsme.types.Base):
    """Transplant task result."""

    #: task id
    task = unicode

    #: state
    state = unicode

    #: new tip id
    tip = unicode

    #: error
    error = unicode
