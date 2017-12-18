"""
A template for an asynchronous task that updates data in Open Humans.

This example task:
  1. deletes any current files in OH if they match the planned upload filename
  2. adds a data file
"""
from __future__ import absolute_import, print_function

import requests


OH_API_BASE = 'https://www.openhumans.org/api/direct-sharing'
OH_EXCHANGE_TOKEN = OH_API_BASE + '/project/exchange-member/'
OH_DELETE_FILES = OH_API_BASE + '/project/files/delete/'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'


def delete_all_oh_files(oh_member):
    """
    Delete all project files matching the filename for this Open Humans member.

    This deletes files this project previously added to the Open Humans
    member account, if they match this filename. Read more about file deletion
    API options here:
    https://www.openhumans.org/direct-sharing/oauth2-data-upload/#deleting-files
    """
    req = requests.post(OH_DELETE_FILES,
                        params={'access_token': oh_member.get_access_token()},
                        data={'project_member_id': oh_member.oh_id,
                              'all_files': True})
