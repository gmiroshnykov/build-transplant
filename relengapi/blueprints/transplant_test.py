import fnmatch
import json
import os
import shutil
import tempfile
import unittest

from flask import Flask
from repository import Repository

from transplant import bp, DEFAULT_USERNAME, DEFAULT_EMAIL
Repository.username = DEFAULT_USERNAME
Repository.email = DEFAULT_EMAIL

class TransplantTestCase(unittest.TestCase):
    def setUp(self):
        self.debug = False

        self.prepare_mock_repositories()
        app = self.prepare_app()
        self.app = app.test_client()

    def prepare_mock_repositories(self):
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.workdir = tempfile.mkdtemp()

        self.src = Repository.init(self.src_dir)
        self.dst = Repository.init(self.dst_dir)

        self._set_test_file_content(self.src_dir, "Hello World!\n")
        self.src.commit("Initial commit", addremove=True)
        self.dst.pull(self.src_dir, update=True)

    def prepare_app(self):
        app = Flask(__name__)
        app.register_blueprint(bp)

        app.config['TRANSPLANT_REPOSITORIES'] = [{
            'name': 'test-src',
            'path': self.src_dir
        }, {
            'name': 'test-dst',
            'path': self.dst_dir
        }]

        app.config['TRANSPLANT_WORKDIR'] = self.workdir

        return app

    def tearDown(self):
        if self.debug:
            print "src_dir: " + self.src_dir
            print "dst_dir: " + self.dst_dir
            print "workdir: " + self.workdir
        else:
            shutil.rmtree(self.src_dir)
            shutil.rmtree(self.dst_dir)
            shutil.rmtree(self.workdir)

    def _set_test_file_content(self, dir, content):
        test_file = os.path.join(dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write(content)

    def _get_test_file_content(self, dir):
        test_file = os.path.join(dir, 'test.txt')
        with open(test_file, 'r') as f:
            return f.read()

    def test_transplant_single_commit(self):
        self._set_test_file_content(self.src_dir, "Goodbye World!\n")
        self.src.commit("Goodbye World!")
        commit = {
            "commit": self.src.id(id=True)
        }

        result = self.app.post('/transplant', data=json.dumps({
            'src': 'test-src',
            'dst': 'test-dst',
            'items': [commit]
        }), content_type='application/json')

        assert result.status_code == 200

        data = json.loads(result.data)
        assert 'tip' in data

        self.dst.update()

        content = self._get_test_file_content(self.dst_dir)
        assert content == "Goodbye World!\n"

    def test_transplant_squashed(self):
        content = "Goodbye World!\n"
        self._set_test_file_content(self.src_dir, content)
        self.src.commit("Goodbye World!")
        commit_id_1 = self.src.id(id=True)

        content += "Hello Again!\n"
        self._set_test_file_content(self.src_dir, content)
        self.src.commit("Hello Again!\n")
        commit_id_2 = self.src.id(id=True)

        result = self.app.post('/transplant', data=json.dumps({
            'src': 'test-src',
            'dst': 'test-dst',
            'items': [{
                'revset': '{}::{}'.format(commit_id_1, commit_id_2)
            }]
        }), content_type='application/json')

        assert result.status_code == 200

        data = json.loads(result.data)
        assert 'tip' in data

        self.dst.update()

        actual_content = self._get_test_file_content(self.dst_dir)
        assert actual_content == content

        commit_info = self.dst.log(rev='tip')[0]
        assert "Goodbye World!" in commit_info['message']
        assert "Hello Again!" in commit_info['message']

    def test_transplant_squashed_message(self):
        content = "Goodbye World!\n"
        self._set_test_file_content(self.src_dir, content)
        self.src.commit("Goodbye World!")
        commit_id_1 = self.src.id(id=True)

        content += "Hello Again!\n"
        self._set_test_file_content(self.src_dir, content)
        self.src.commit("Hello Again!\n")
        commit_id_2 = self.src.id(id=True)

        result = self.app.post('/transplant', data=json.dumps({
            'src': 'test-src',
            'dst': 'test-dst',
            'items': [{
                'revset': '{}::{}'.format(commit_id_1, commit_id_2),
                'message': 'I am squashed!'
            }]
        }), content_type='application/json')

        assert result.status_code == 200

        data = json.loads(result.data)
        assert 'tip' in data

        self.dst.update()

        actual_content = self._get_test_file_content(self.dst_dir)
        assert actual_content == content

        commit_info = self.dst.log(rev='tip')[0]
        assert commit_info['message'] == 'I am squashed!'

    def test_change_messsage(self):
        self._set_test_file_content(self.src_dir, "Goodbye World!\n")
        self.src.commit("Goodbye World!")

        commit = {
            "commit": self.src.id(id=True),
            "message": "Goodbye World! a=me"
        }

        result = self.app.post('/transplant', data=json.dumps({
            'src': 'test-src',
            'dst': 'test-dst',
            'items': [commit]
        }), content_type='application/json')

        assert result.status_code == 200

        data = json.loads(result.data)
        assert 'tip' in data

        self.dst.update()

        content = self._get_test_file_content(self.dst_dir)
        assert content == "Goodbye World!\n"

        commit_info = self.dst.log(rev='tip')[0]

        assert commit_info['message'] == "Goodbye World! a=me"

    def test_error_conflict(self):
        content = "Goodbye World!\n"
        self._set_test_file_content(self.dst_dir, content)
        self.dst.commit("Goodbye World!")

        content = "Hello again!\n"
        self._set_test_file_content(self.src_dir, content)
        self.src.commit("Hello again!")

        commit = {
            "commit": self.src.id(id=True)
        }

        result = self.app.post('/transplant', data=json.dumps({
            'src': 'test-src',
            'dst': 'test-dst',
            'items': [commit]
        }), content_type='application/json')

        assert result.status_code == 409

        data = json.loads(result.data)
        assert data['error'] == 'Transplant failed'
        assert 'details' in data

        # check that content is not updated
        self.dst.update()

        actual_content = self._get_test_file_content(self.dst_dir)
        assert content != actual_content

        # check that there are no .rej leftovers
        rejects = []
        workdir = os.path.join(self.workdir, 'test-dst')
        for root, dirnames, filenames in os.walk(workdir):
            for filename in fnmatch.filter(filenames, '*.rej'):
                rejects.append(os.path.join(root, filename))

        assert len(rejects) == 0

if __name__ == '__main__':
    unittest.main()
