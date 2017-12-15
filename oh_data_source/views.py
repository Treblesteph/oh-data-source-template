import logging
import os
import json

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
import requests

from urllib2 import HTTPError

from .models import OpenHumansMember
from .tasks import handle_uploaded_file, delete_all_oh_files
from .forms import UploadFileForm

OH_CLIENT_ID = os.getenv('OH_CLIENT_ID', '')
OH_CLIENT_SECRET = os.getenv('OH_CLIENT_SECRET', '')

OH_API_BASE = 'https://www.openhumans.org/api/direct-sharing'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'

# Open Humans settings
OH_BASE_URL = 'https://www.openhumans.org'

APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://127.0.0.1:5000')
APP_PROJ_PAGE = 'https://www.openhumans.org/activity/seeq/'

# Set up logging.
logger = logging.getLogger(__name__)


def oh_get_member_data(token):
    """
    Exchange OAuth2 token for member data.
    """
    req = requests.get(
        '{}/api/direct-sharing/project/exchange-member/'.format(OH_BASE_URL),
        params={'access_token': token})
    if req.status_code == 200:
        return req.json()
    raise Exception('Status code {}'.format(req.status_code))
    return None


def oh_code_to_member(code):
    """
    Exchange code for token, use this to create and return OpenHumansMember.

    If a matching OpenHumansMember already exists in db, update and return it.
    """
    if settings.OH_CLIENT_SECRET and settings.OH_CLIENT_ID and code:
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': '{}/complete'.format(APP_BASE_URL),
            'code': code,
        }
        req = requests.post(
            '{}/oauth2/token/'.format(OH_BASE_URL),
            data=data,
            auth=requests.auth.HTTPBasicAuth(
                settings.OH_CLIENT_ID,
                settings.OH_CLIENT_SECRET
            ))
        data = req.json()
        if 'access_token' in data:
            oh_id = oh_get_member_data(
                data['access_token'])['project_member_id']
            try:
                oh_member = OpenHumansMember.objects.get(oh_id=oh_id)
                logger.debug('Member {} re-authorized.'.format(oh_id))
                oh_member.access_token = data['access_token']
                oh_member.refresh_token = data['refresh_token']
                oh_member.token_expires = OpenHumansMember.get_expiration(
                    data['expires_in'])
            except OpenHumansMember.DoesNotExist:
                oh_member = OpenHumansMember.create(
                    oh_id=oh_id,
                    access_token=data['access_token'],
                    refresh_token=data['refresh_token'],
                    expires_in=data['expires_in'])
                logger.debug('Member {} created.'.format(oh_id))
            oh_member.save()

            return oh_member
        elif 'error' in req.json():
            logger.debug('Error in token exchange: {}'.format(req.json()))
        else:
            logger.warning('Neither token nor error info in OH response!')
    else:
        print('OH_CLIENT_SECRET:')
        print(OH_CLIENT_SECRET)
        print('code:')
        print(code)
        logger.error('OH_CLIENT_SECRET or code are unavailable')
    return None


def index(request):
    """
    Starting page for app.
    """
    context = {'client_id': settings.OH_CLIENT_ID,
               'oh_proj_page': settings.OH_ACTIVITY_PAGE}

    return render(request, 'oh_data_source/index.html', context=context)


def complete(request):
    """
    Receive user from Open Humans. Store data, start data upload task.
    """

    logger.debug("Received user returning from Open Humans.")

    # Exchange code for token.
    # This creates an OpenHumansMember and associated User account.
    if request.method == 'GET':
        code = request.GET.get('code', '')
        print("code in get:")
        print(code)
        oh_member = oh_code_to_member(code=code)
        print("oh_member")
        print(oh_member)

        # Log in the user.
        # (You may want this if connecting user with another OAuth process.)
        user = oh_member.user
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')

        context = {'oh_member': oh_member,
                   'code': code}
        return render(request, 'oh_data_source/complete.html',
                      context=context)

    if request.method == 'POST':
        print('running POST handling bit')

        oh_member = request.user.openhumansmember
        print(oh_member.oh_id)
        print('oh member:')
        print(oh_member)

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('form is valid')
            handle_uploaded_file(request.FILES['file'])

            # Initiate a data transfer task, then render 'complete.html'.

            upload_file_to_oh(request.user.openhumansmember,
                              request.FILES['file'])

            # xfer_to_open_humans(request.FILES['file'],
            #                     oh_id=oh_member.oh_id)
            context = {'oh_id': oh_member.oh_id,
                       'oh_proj_page': settings.OH_ACTIVITY_PAGE}
            return render(request, 'oh_data_source/complete.html',
                          context=context)
            # return HttpResponseRedirect(reverse('complete'))
        else:
            print('form not valid')
    else:
        form = UploadFileForm()

        return render(request, 'oh_data_source/complete.html')

    logger.debug('Invalid code exchange. User returned to starting page.')
    return redirect('/')


def upload_file_to_oh(oh_member, filehandle):
    """
    This demonstrates using the Open Humans "large file" upload process.

    The small file upload process is simpler, but it can time out. This
    alternate approach is required for large files, and still appropriate
    for small files.

    This process is "direct to S3" using three steps: 1. get S3 target URL from
    Open Humans, 2. Perform the upload, 3. Notify Open Humans when complete.
    """
    metadata = {
        'tags': ['twitter', 'archive'],
        'description': 'Archive tweets and metadata downloaded from twitter',
    }

    delete_all_oh_files(oh_member)

    # Get the S3 target from Open Humans.
    upload_url = '{}?access_token={}'.format(
        OH_DIRECT_UPLOAD, oh_member.get_access_token())
    print("s3 bit:")
    print(upload_url)
    print(oh_member.oh_id)

    req1 = requests.post(
        upload_url,
        data={'project_member_id': oh_member.oh_id,
              'filename': filehandle.name,
              'metadata': json.dumps(metadata)})

    if req1.status_code != 201:
        raise HTTPError(upload_url, req1.status_code,
                        'Bad response when starting file upload.')
    # Upload to S3 target.
    # with open(filepath, 'rb') as fh:
    req2 = requests.put(url=req1.json()['url'], data=filehandle)

    if req2.status_code != 200:
        raise HTTPError(req1.json()['url'], req2.status_code,
                        'Bad response when uploading to target.')

    # Report completed upload to Open Humans.
    complete_url = ('{}?access_token={}'.format(
        OH_DIRECT_UPLOAD_COMPLETE, oh_member.get_access_token()))
    req3 = requests.post(
        complete_url,
        data={'project_member_id': oh_member.oh_id,
              'file_id': req1.json()['id']})
    if req3.status_code != 200:
        raise HTTPError(complete_url, req2.status_code,
                        'Bad response when completing upload.')

    print('Upload done: "{}" for member {}.'.format(
          'django_test.txt', oh_member.oh_id))
