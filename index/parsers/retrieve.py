import sys
import json
import logging
import argparse

import requests

from index import errors


def retrieve_record(did, **kwargs):
    '''
    Retrieve a record by id.
    '''
    resource = 'http://localhost:8080/index/{did}'.format(did=did)

    res = requests.get(resource)

    try: res.raise_for_status()
    except Exception as err:
        raise errors.BaseIndexError(res.status_code, res.text)

    try: doc = res.json()
    except ValueError as err:
        reason = json.dumps({'error': 'invalid json payload returned'})
        raise errors.BaseIndexError(res.status_code, reason)

    sys.stdout.write(json.dumps(doc))


def config(parser):
    '''
    Configure the retrieve command.
    '''
    parser.set_defaults(func=retrieve_record)

    parser.add_argument('did',
        help='id of record to retrieve',
    )