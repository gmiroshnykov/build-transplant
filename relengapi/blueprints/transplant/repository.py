# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pipes
import subprocess
import xml.etree.ElementTree as ET

import rest

def mkdirp(fullpath):
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)


class Repository(object):
    cmd = "hg"
    registered_extensions = {}

    def __init__(self, path):
        self.path = path

    @staticmethod
    def unsafe_command(cmd, **kwargs):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        stdout, stderr = p.communicate()
        return p.returncode, stdout, stderr

    @classmethod
    def register_extension(cls, name, path):
        cls.registered_extensions[name] = path

    @classmethod
    def command(cls, args, extensions=None, **kwargs):
        cmd = [cls.cmd]

        extensions_config = cls._get_extensions_config(extensions)
        cmd.extend(extensions_config)
        cmd.extend(args)

        returncode, stdout, stderr = cls.unsafe_command(cmd, **kwargs)
        if returncode != 0:
            raise MercurialException(cmd, returncode, stdout, stderr)

        return stdout

    @classmethod
    def _get_extensions_config(cls, extensions):
        if extensions is None:
            return []

        extensions_config = []
        for extension in extensions:
            if extension in cls.registered_extensions:
                path = cls.registered_extensions[extension]
            else:
                path = ""

            extensions_config.extend(['--config', 'extensions.{}={}'.format(extension, path)])

        return extensions_config

    @classmethod
    def clone(cls, source, destination, rev=None):
        mkdirp(destination)
        cmd = ['clone']

        if rev:
            if not isinstance(rev, list):
                rev = [rev]

            for r in rev:
                cmd.extend(['--rev', r])

        cmd.extend([source, destination])

        cls.command(cmd)
        return Repository(destination)

    @classmethod
    def init(cls, destination):
        mkdirp(destination)
        cls.command(['init'], cwd=destination)
        return Repository(destination)

    def local_command(self, args, **kwargs):
        return self.command(args, cwd=self.path, **kwargs)

    def id(self, **kwargs):
        cmd = ['id']

        if 'id' in kwargs:
            cmd.append('--id')

        return self.local_command(cmd).strip()

    def pull(self, source=None, update=False, rev=False):
        cmd = ['pull']

        if update:
            cmd.append('--update')

        if rev:
            if not isinstance(rev, list):
                rev = [rev]

            for r in rev:
                cmd.extend(['--rev', r])

        if source:
            cmd.append(source)

        self.local_command(cmd)

    def push(self):
        try:
            return self.local_command(['push'])
        except MercurialException, e:
            if e.returncode == 1:
                return e.stdout
            else:
                raise e

    def log(self, **kwargs):
        output = self.raw_log(style='xml', **kwargs)

        if output == "":
            return []

        results = []
        root = ET.fromstring(output)
        for logentry in root.iter('logentry'):
            node = logentry.get('node')
            date = logentry.find('date').text
            message = logentry.find('msg').text
            xmlAuthor = logentry.find('author')
            author_name = xmlAuthor.text
            author_email = xmlAuthor.get('email')

            # I hate Mercurial
            if author_name == author_email:
                author = author_name
            else:
                author = author_name + ' <' + author_email + '>'

            result = rest.CommitInfo(
                node=node,
                date=date,
                author=author,
                message=message
            )
            results.append(result)
        return results

    def raw_log(self, rev=None, style=None, **kwargs):
        cmd = ['log']

        if rev:
            if not isinstance(rev, list):
                rev = [rev]

            for r in rev:
                cmd.extend(['--rev', r])

        if style:
            cmd.extend(['--style', style])

        try:
            return self.local_command(cmd, **kwargs)
        except MercurialException, e:
            if 'abort: unknown revision' in e.stderr:
                raise UnknownRevisionException(rev, cause=e)
            else:
                raise e

    def transplant(self, revset, source=None, filter=None, **kwargs):
        cmd = ['transplant']

        if source:
            cmd.extend(['--source', source])

        if filter:
            cmd.extend(['--filter', filter])

        if isinstance(revset, list):
            cmd.extend(revset)
        else:
            cmd.append(revset)

        return self.local_command(cmd, extensions=['transplant'], **kwargs)

    def commit(self, message, addremove=False, user=None):
        cmd = ['commit', '--message', message]

        if addremove:
            cmd.append('--addremove')

        if user:
            cmd.extend(['--user', user])

        return self.local_command(cmd)

    def update(self, clean=False):
        cmd = ['update']

        if clean:
            cmd.append('--clean')

        return self.local_command(cmd)

    def purge(self, abort_on_err=False, all=False):
        cmd = ['purge']

        if abort_on_err:
            cmd.append('--abort-on-err')

        if all:
            cmd.append('--all')

        return self.local_command(cmd, extensions=['purge'])

    def strip(self, rev, no_backup=False):
        cmd = ['strip', '--rev', rev]

        if no_backup:
            cmd.append('--no-backup')

        return self.local_command(cmd, extensions=['strip'])

    def collapse(self, rev, message=None, user=None):
        cmd = ['collapse', '--rev', rev]

        env = os.environ.copy()
        if message is None:
            env['EDITOR'] = 'true'
        else:
            cmd.extend(['--message', message])

        if user is not None:
            env['HGUSER'] = user

        return self.local_command(cmd, env=env, extensions=['collapse'])

    def set_config(self, config):
        output = ""
        for section, options in config.iteritems():
            output += "[" + section + "]\n"
            for k, v in options.iteritems():
                output += k + " = " + v + "\n"

        filename = self.path + "/.hg/hgrc"
        with open(filename, "w") as f:
            f.write(output)


class MercurialException(Exception):
    def __init__(self, cmd, returncode, stdout, stderr):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        Exception.__init__(self, cmd, returncode, stdout, stderr)

    def __str__(self):
        command = ' '.join([pipes.quote(arg) for arg in self.cmd])
        return ("command: {}\n" +
                "returncode: {}\n" +
                "stdout: {}\n" +
                "stderr: {}\n").format(command, self.returncode, self.stdout, self.stderr)


class UnknownRevisionException(Exception):
    def __init__(self, rev, cause=None):
        self.rev = rev
        self.cause = cause
        Exception.__init__(self, rev, cause)

    def __str__(self):
        message = "unknown revision: '{}'".format(self.rev)
        if self.cause is not None:
            message = message + "\ncaused by\n" + str(self.cause)
        return message
