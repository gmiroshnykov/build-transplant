import os
import json
import time
import tempfile
import shutil
from nose.tools import eq_
from relengapi.lib.testing.context import TestContext
from repository import Repository
from kombu import Exchange, Queue

test_temp_dir = tempfile.mkdtemp()

def teardown_module():
    if os.path.exists(test_temp_dir):
        shutil.rmtree(test_temp_dir)

def app_setup(app):
    app.config['CELERY_ACCEPT_CONTENT'] = ['json']
    app.config['CELERY_TASK_SERIALIZER'] = 'json'
    app.config['CELERY_RESULT_SERIALIZER'] = 'json'
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/2'
    app.config['CELERY_BACKEND'] = 'redis://localhost:6379/3'
    app.config['CELERY_QUEUES'] = (
        Queue('transplant', Exchange('transplant'), routing_key='transplant'),
    )

    app.src_dir = tempfile.mkdtemp(dir=test_temp_dir)
    app.dst_dir = tempfile.mkdtemp(dir=test_temp_dir)
    app.config['TRANSPLANT_WORKDIR'] = tempfile.mkdtemp(dir=test_temp_dir)
    app.config['TRANSPLANT_REPOSITORIES'] = [{
        'name': 'test-src',
        'path': app.src_dir
    }, {
        'name': 'test-dst',
        'path': app.dst_dir
    }]

    app.src = Repository.init(app.src_dir)
    app.dst = Repository.init(app.dst_dir)

    _set_test_file_content(app.src_dir, "Hello World!\n")
    app.src.commit("Initial commit", addremove=True, user="Test User")
    app.dst.pull(app.src_dir, update=True)

def _set_test_file_content(dir, content):
    test_file = os.path.join(dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write(content)

def _get_test_file_content(dir):
    test_file = os.path.join(dir, 'test.txt')
    with open(test_file, 'r') as f:
        return f.read()


def _wait_until_task_ready(client, task_id, attempts=10, interval=0.5):
    attempt = attempts
    while attempt > 0:
        attempt = attempt - 1

        rv = client.get('/transplant/status?task={}'.format(task_id))
        eq_(rv.status_code, 200)

        response = json.loads(rv.data)
        if response['state'] != 'PENDING':
            return response

        time.sleep(interval)

    raise RuntimeError('task is not ready after {} attemps'.format(attempts))


test_context = TestContext(app_setup=app_setup, config={
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_BROKER_URL': 'redis://localhost:6379/2',
    'CELERY_BACKEND': 'redis://localhost:6379/3',
})

@test_context
def test_lookup(app, client):
    commit_info = app.src.log(rev='tip')[0]

    rv = client.get(
        '/transplant/repositories/test-src/lookup?revset={}'.format(commit_info['node'])
    )
    eq_(rv.status_code, 200)

    actual_data = json.loads(rv.data)
    assert 'revset' in actual_data
    assert 'commits' in actual_data['revset']
    eq_(len(actual_data['revset']['commits']), 1)

    actual_commit = actual_data['revset']['commits'][0]
    assert 'node' in actual_commit
    assert 'author' in actual_commit
    assert 'date' in actual_commit
    assert 'message' in actual_commit
    eq_(actual_commit['node'], commit_info['node'])


@test_context
def test_lookup_unknown_repository(app, client):
    rv = client.get('/transplant/repositories/unknown/lookup?revset=tip')
    eq_(rv.status_code, 400)

    actual_data = json.loads(rv.data)
    eq_(actual_data['error'], 'unknown repository: unknown')


@test_context
def test_transplant_single_commit(app, client):
    _set_test_file_content(app.src_dir, "Goodbye World!\n")
    app.src.commit("Goodbye World!", user="Test User")
    commit = {
        "commit": app.src.id(id=True)
    }

    rv = client.post_json('/transplant/transplant', {
        'src': 'test-src',
        'dst': 'test-dst',
        'items': [commit]
    })
    eq_(rv.status_code, 200)

    response = json.loads(rv.data)
    task_id = response['task']

    response = _wait_until_task_ready(client, task_id)

    eq_(response, '')
