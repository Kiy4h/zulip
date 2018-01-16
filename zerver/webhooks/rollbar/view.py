from django.utils.translation import ugettext as _
from zerver.lib.actions import check_send_stream_message
from zerver.lib.response import json_success, json_error
from zerver.decorator import REQ, has_request_variables, api_key_only_webhook_view
from zerver.lib.validator import check_dict, check_string

from zerver.models import Client, UserProfile

from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Iterable, Optional, Text
import requests

ROLLBAR_MESSAGE_TYPE = {
    'exp_repeat_item': '{item_count} {item_level}: ',
    'occurrence': '',
    'item_velocity': '{item_count} occurrences in {minutes}: ',
    'new_item': 'New Error: ',
    'reactivated_item': 'Reactivated {item_level}: ',
    'reopened_item': 'Reopened by {user_name}: ',
    'resolved_item': 'Resolved by {user_name}: ',
}

@api_key_only_webhook_view('Rollbar')
@has_request_variables
def api_rollbar_webhook(request: HttpRequest, user_profile: UserProfile,
                        payload: Dict[str, Iterable[Dict[str, Any]]]=REQ(argument_type='body'),
                        stream: Text=REQ(default='test'),
                        topic: Text=REQ(default='Rollbar')) -> HttpResponse:
    item_level = payload['data']['item']['last_occurrence']['level'].title()
    uuid = payload['data']['item']['last_occurrence']['uuid']
    environment = payload['data']['item']['environment']
    event = payload['event_name']
    req = requests.get('https://rollbar.com/item/uuid/?uuid=' + uuid, allow_redirects=False)
    req_url = req.url
    print("REQUEST URL:", req_url, "\nSTATUS CODE:", req.status_code, "\nHEADERS:", req.headers)
    req_url_split = req_url.replace('/', ' ').split()
    user_name = req_url_split[2].title()
    project_name = req_url_split[3]
    tmp_message = ROLLBAR_MESSAGE_TYPE[event]

    if event == 'exp_repeat_item':
        tmp_message = tmp_message.format(item_count=payload['data']['occurrences'],
                                         item_level=item_level)
    if event == 'item_velocity':
        tmp_message = tmp_message.format(item_count=payload['data']['trigger']['threshold'],
                                         minutes=payload['data']['trigger']['window_size_description'])
    if 'item_level' in event:
        tmp_message = tmp_message.format(item_level=item_level)
    if 'user_name' in event:
        tmp_message = tmp_message.format(user_name=user_name)

    body = '[{}] {environment} - {message_type}{item_name}'.format(
        project_name,
        environment=environment,
        message_type=tmp_message,
        item_name=payload['data']['item']['title'])

    if event == 'occurrence':
        body += '({})'.format(item_level)
    body += '\n' + req_url

    check_send_stream_message(user_profile, request.client,
                              stream, topic, body)

    return json_success()
