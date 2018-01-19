# encoding: utf-8

'''
Code for generating email notifications for users (e.g. email notifications for
new activities in your dashboard activity stream) and emailing them to the
users.

'''
import datetime
import re
import logging

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h

from ckan.lib.search import SearchError, SearchQueryError
from ckan.lib.dictization import model_dictize
from ckan.lib.dictization import model_save
from ckan.common import ungettext, config
from paste.deploy.converters import asbool

log = logging.getLogger(__name__)

def string_to_timedelta(s):
    '''Parse a string s and return a standard datetime.timedelta object.

    Handles days, hours, minutes, seconds, and microseconds.

    Accepts strings in these formats:

    2 days
    14 days
    4:35:00 (hours, minutes and seconds)
    4:35:12.087465 (hours, minutes, seconds and microseconds)
    7 days, 3:23:34
    7 days, 3:23:34.087465
    .087465 (microseconds only)

    :raises ckan.logic.ValidationError: if the given string does not match any
        of the recognised formats

    '''
    patterns = []
    days_only_pattern = '(?P<days>\d+)\s+day(s)?'
    patterns.append(days_only_pattern)
    hms_only_pattern = '(?P<hours>\d?\d):(?P<minutes>\d\d):(?P<seconds>\d\d)'
    patterns.append(hms_only_pattern)
    ms_only_pattern = '.(?P<milliseconds>\d\d\d)(?P<microseconds>\d\d\d)'
    patterns.append(ms_only_pattern)
    hms_and_ms_pattern = hms_only_pattern + ms_only_pattern
    patterns.append(hms_and_ms_pattern)
    days_and_hms_pattern = '{0},\s+{1}'.format(days_only_pattern,
            hms_only_pattern)
    patterns.append(days_and_hms_pattern)
    days_and_hms_and_ms_pattern = days_and_hms_pattern + ms_only_pattern
    patterns.append(days_and_hms_and_ms_pattern)

    for pattern in patterns:
        match = re.match('^{0}$'.format(pattern), s)
        if match:
            break

    if not match:
        raise logic.ValidationError('Not a valid time: {0}'.format(s))

    gd = match.groupdict()
    days = int(gd.get('days', '0'))
    hours = int(gd.get('hours', '0'))
    minutes = int(gd.get('minutes', '0'))
    seconds = int(gd.get('seconds', '0'))
    milliseconds = int(gd.get('milliseconds', '0'))
    microseconds = int(gd.get('microseconds', '0'))
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes,
            seconds=seconds, milliseconds=milliseconds,
            microseconds=microseconds)
    return delta

def _notifications_for_saved_searches(activities, user_dict):
    '''Return one or more email notifications covering the given searches.

    This function handles grouping multiple searches into a single digest
    email.

    :param activities: the searches to consider
    :type searches: list of activity dicts like those returned by
        ckan.logic.action.get.dashboard_activity_list()

    :returns: a list of email notifications
    :rtype: list of dicts each with keys 'subject' and 'body'

    '''
    if not activities:
        return []

    if not user_dict.get('activity_streams_email_notifications'):
        return []

    subject = "New result information from " + config.get('ckan.site_title')
    body = base.render(
            'activity_streams/saved_searches_email_notifications.text',
            extra_vars={'activities': activities})
    notifications = [{
        'subject': subject,
        'body': body
        }]

    return notifications

def _notifications_for_activities(activities, user_dict):
    '''Return one or more email notifications covering the given activities.

    This function handles grouping multiple activities into a single digest
    email.

    :param activities: the activities to consider
    :type activities: list of activity dicts like those returned by
        ckan.logic.action.get.dashboard_activity_list()

    :returns: a list of email notifications
    :rtype: list of dicts each with keys 'subject' and 'body'

    '''
    if not activities:
        return []

    if not user_dict.get('activity_streams_email_notifications'):
        return []

    # We just group all activities into a single "new activity" email that
    # doesn't say anything about _what_ new activities they are.
    # TODO: Here we could generate some smarter content for the emails e.g.
    # say something about the contents of the activities, or single out
    # certain types of activity to be sent in their own individual emails,
    # etc.
    subject = ungettext(
        "{n} new activity from {site_title}",
        "{n} new activities from {site_title}",
        len(activities)).format(
                site_title=config.get('ckan.site_title'),
                n=len(activities))
    body = base.render(
            'activity_streams/activity_stream_email_notifications.text',
            extra_vars={'activities': activities})
    notifications = [{
        'subject': subject,
        'body': body
        }]

    return notifications

def _make_parameters(query_string):
    parts = query_string.split("&")
    res = []
    for part in parts:
        s = part.split("=")
        if len(s) > 1:
            res.append((s[0], s[1]))
    return res

def _notifications_from_saved_searches(user_dict, since):
    def make_url(parts):
        #Get rid of last & - but there really should always be at least one param... so not necessary
        if len(parts['end']) > 0:
            parts['end'] = parts['end'][0:len(parts['end'])-1]
        return parts['base'] + "?" + parts['end']
    # Note we ignore "since" here as we aren't going to
    # look at when the search changed
    context = {'model': model, 'session': model.Session,
            'user': user_dict['id']}
    # FIXME: same comment as below regarding direct
    # access to model applies here - move to logic
    _search_list = model.saved_search.user_saved_searches_list(user_dict['id']) 
    search_list = model_dictize.saved_search_list_dictize(_search_list, context)
    activity_list = []
    for search in search_list:
        #save link to search (needed for activity later)
        try:
            if True:
                fq = ''
                q = ''
                search_extras = {}
                reconstruct_search = {}
                reconstruct_search['end'] = ""
                for (param, value) in _make_parameters(search['search_string'].replace("?","")):
                    if param not in ['q', 'page', 'sort'] \
                            and len(value) and not param.startswith('_'):
                        reconstruct_search['end'] += param + "=" + value + "&" 
                        if not param.startswith('ext_'):
                            if param == "organization":
                                param = "owner_org"
                            fq += ' %s:"%s"' % (param, value)
                        else:
                            search_extras[param] = value
                    elif param == 'q':
                        q = value
                    elif param == '_search_organization' and value != '0':
                        fq += ' owner_org:%s' % (value)
                        reconstruct_search['base'] = h.url_for(controller='organization', action='read', id=value, qualified=True)
                    elif param == '_search_group' and value != '0':
                        fq += ' groups:%s' % (value)
                        reconstruct_search['base'] = h.url_for(controller='group', action='read', id=value, qualified=True)
                    elif param == '_search_package_type' and value != '0':
                        package_type = value
                        type_is_search_all = h.type_is_search_all(package_type)
                        reconstruct_search['base'] = h.url_for(controller='package', action='search', package_type=value, qualified=True)

                        if not type_is_search_all:
                        # Only show datasets of this particular type
                            fq += ' +dataset_type:{type}'.format(type=package_type)
                
                data_dict = {
                    'q': q,
                    'fq': fq.strip(),
                    'rows': 1000,
                    'extras': search_extras,
                    'include_private': asbool(config.get(
                    'ckan.search.default_include_private', True)),
                }

                query = logic.get_action('package_search')(context, data_dict)
                ids = set()
                for result in query['results']:
                    ids.add(result['id'])
                if search['last_run']:
                    last_ids = search['last_results']
                    last_ids = set(last_ids)
                    difference = len(ids - last_ids);
                    if difference > 0: 
                        activity = {'data': {'search_url': make_url(reconstruct_search), 'activity_type': 'search_results_changed'}}
                        activity_list.append(activity)
                    else:
                        # For each result, ceheck if metmod more than last run, then break zes
                        resultchange = False
                        for result in query['results']:
                            fmt = '%Y-%m-%dT%H:%M:%S.%f'
                            if datetime.datetime.strptime(result['metadata_modified'], fmt) >  datetime.datetime.strptime(search['last_run'], fmt):
                                activity = {'data': {'search_url': make_url(reconstruct_search), 'activity_type': 'search_results_updated'}}
                                activity_list.append(activity)
                                break
            
                search['last_results'] = list(ids)
                search['last_run'] = datetime.datetime.utcnow()
 
                model_save.saved_search_dict_save(search, context)

                if not context.get('defer_commit'):
                    model.repo.commit()
            
        except SearchQueryError, se:
            # FIXME: Ideally, tell user about this so they can delete/edit
            log.error('Dataset search query rejected: %r', se.args)
        except SearchError, se:
            # FIXME: Ideally, tell user about this so they can delete/edit/inform admin
            log.error('Dataset search error: %r', se.args) 

    return _notifications_for_saved_searches(activity_list, user_dict)
    #TODO Make results look like activities
    #TODO undo return stuff everywhere

def _notifications_from_dashboard_activity_list(user_dict, since):
    '''Return any email notifications from the given user's dashboard activity
    list since `since`.

    '''
    # Get the user's dashboard activity stream.
    context = {'model': model, 'session': model.Session,
            'user': user_dict['id']}
    activity_list = logic.get_action('dashboard_activity_list')(context, {})

    # Filter out the user's own activities., so they don't get an email every
    # time they themselves do something (we are not Trac).
    activity_list = [activity for activity in activity_list
            if activity['user_id'] != user_dict['id']]

    # Filter out the old activities.
    strptime = datetime.datetime.strptime
    fmt = '%Y-%m-%dT%H:%M:%S.%f'
    activity_list = [activity for activity in activity_list
            if strptime(activity['timestamp'], fmt) > since]

    return _notifications_for_activities(activity_list, user_dict)




# A list of functions that provide email notifications for users from different
# sources. Add to this list if you want to implement a new source of email
# notifications.
_notifications_functions = [
    _notifications_from_dashboard_activity_list,
    _notifications_from_saved_searches
    ]


def get_notifications(user_dict, since):
    '''Return any email notifications for the given user since `since`.

    For example email notifications about activity streams will be returned for
    any activities the occurred since `since`.

    :param user_dict: a dictionary representing the user, should contain 'id'
        and 'name'
    :type user_dict: dictionary

    :param since: datetime after which to return notifications from
    :rtype since: datetime.datetime

    :returns: a list of email notifications
    :rtype: list of dicts with keys 'subject' and 'body'

    '''
    notifications = []
    for function in _notifications_functions:
        notifications.extend(function(user_dict, since))
    return notifications


def send_notification(user, email_dict):
    '''Email `email_dict` to `user`.'''
    import ckan.lib.mailer

    if not user.get('email'):
        # FIXME: Raise an exception.
        return

    try:
        ckan.lib.mailer.mail_recipient(user['display_name'], user['email'],
                email_dict['subject'], email_dict['body'])
    except ckan.lib.mailer.MailerException:
        raise


def get_and_send_notifications_for_user(user):

    # Parse the email_notifications_since config setting, email notifications
    # from longer ago than this time will not be sent.
    email_notifications_since = config.get(
            'ckan.email_notifications_since', '2 days')
    email_notifications_since = string_to_timedelta(
            email_notifications_since)
    email_notifications_since = (datetime.datetime.utcnow()
            - email_notifications_since)

    # FIXME: We are accessing model from lib here but I'm not sure what
    # else to do unless we add a get_email_last_sent() logic function which
    # would only be needed by this lib.
    email_last_sent = model.Dashboard.get(user['id']).email_last_sent
    activity_stream_last_viewed = (
            model.Dashboard.get(user['id']).activity_stream_last_viewed)

    since = max(email_notifications_since, email_last_sent,
            activity_stream_last_viewed)

    notifications = get_notifications(user, since)
    # TODO: Handle failures from send_email_notification.
    for notification in notifications:
        send_notification(user, notification)

    # FIXME: We are accessing model from lib here but I'm not sure what
    # else to do unless we add a update_email_last_sent()
    # logic function which would only be needed by this lib.
    dash = model.Dashboard.get(user['id'])
    dash.email_last_sent = datetime.datetime.utcnow()
    model.repo.commit()

def get_and_send_notifications_for_all_users():
    context = {'model': model, 'session': model.Session, 'ignore_auth': True,
            'keep_email': True}
    users = logic.get_action('user_list')(context, {})
    
    for user in users:
        get_and_send_notifications_for_user(user)

