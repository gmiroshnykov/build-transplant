# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request
from repository import MercurialException
from repository import Repository
from repository import UnknownRevisionException

import tasks
import actions

logger = logging.getLogger(__name__)
bp = Blueprint('transplant', __name__)

@bp.route('/repositories/<repository_id>/lookup')
def flask_lookup(repository_id):
    revset = request.values.get('revset')
    if not revset:
        return jsonify({'error': 'No revset'}), 400

    try:
        revset_info = actions.get_revset_info(repository_id, revset)
    except actions.TooManyCommitsError, e:
        return jsonify({
            'error': e.message
        }), 400
    except actions.TransplantError, e:
        return jsonify({
            'error': e.message
        }), 400
    except MercurialException, e:
        return jsonify({
            'error': e.stderr
        }), 400

    return jsonify({
        'revset': revset_info
    })


@bp.route('/transplant', methods=['POST'])
def flask_transplant():
    params = request.get_json()
    if not params:
        return jsonify({'error': 'No params'}), 400

    src = params.get('src')
    dst = params.get('dst')
    items = params.get('items')

    if not src:
        return jsonify({'error': 'No src'}), 400

    if not dst:
        return jsonify({'error': 'No dst'}), 400

    if not items:
        return jsonify({'error': 'No items'}), 400

    if not actions.has_repo(src):
        msg = 'Unknown src repository: {}'.format(src)
        return jsonify({'error': msg}), 400

    if not actions.has_repo(dst):
        msg = 'Unknown dst repository: {}'.format(dst)
        return jsonify({'error': msg}), 400

    if not actions.is_allowed_transplant(src, dst):
        msg = 'Transplant from {} to {} is not allowed'.format(src, dst)
        return jsonify({'error': msg}), 400

    task = tasks.transplant.apply_async((src, dst, items), queue='transplant')
    return jsonify({
        'task': task.id
    })

@bp.route('/status')
def flask_status():
    task_id = request.values.get('task')

    if not task_id:
        return jsonify({'error': 'No task'}), 400

    task = current_app.celery.AsyncResult(task_id)

    result = {
        'id': task.id,
        'state': task.state
    }

    if task.ready():
        try:
            value = task.get()
            if 'error' in value:
                result['error'] = value['error']
            else:
                result['result'] = value
        except Exception, e:
            result['error'] = e.message

    return jsonify(result)
