"""
sentry.plugins.sentry_useragents.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from ua_parser.user_agent_parser import Parse
import sentry

from django.utils.translation import ugettext_lazy as _

from sentry.plugins import register
from sentry.plugins.bases.tag import TagPlugin


class UserAgentPlugin(TagPlugin):
    version = sentry.VERSION
    author = "Sentry Team"
    author_url = "https://github.com/getsentry/sentry"
    project_default_enabled = True

    def get_tag_values(self, event):
        http = event.interfaces.get('sentry.interfaces.Http')
        if not http:
            return []
        if not http.headers:
            return []
        if 'User-Agent' not in http.headers:
            return []
        ua = Parse(http.headers['User-Agent'])
        if not ua:
            return []
        result = self.get_tag_from_ua(ua)
        if not result:
            return []
        return [result]


class BrowserPlugin(UserAgentPlugin):
    """
    Automatically adds the 'browser' tag from events containing interface data
    from ``sentry.interfaces.Http``.
    """
    slug = 'browsers'
    title = _('Auto Tag: Browsers')
    tag = 'browser'
    tag_label = _('Browser Name')

    def get_tag_from_ua(self, ua):
        ua = ua['user_agent']

        if not ua['family']:
            return

        version = '.'.join(value for value in [
            ua['major'],
            ua['minor'],
        ] if value)
        tag = ua['family']
        if version:
            tag += ' ' + version

        return tag

register(BrowserPlugin)


class OsPlugin(UserAgentPlugin):
    """
    Automatically adds the 'os' tag from events containing interface data
    from ``sentry.interfaces.Http``.
    """
    slug = 'os'
    title = _('Auto Tag: Operating Systems')
    tag = 'os'
    tag_label = _('Operating System')

    def get_tag_from_ua(self, ua):
        ua = ua['os']

        if not ua['family']:
            return

        version = '.'.join(value for value in [
            ua['major'],
            ua['minor'],
            ua['patch'],
        ] if value)
        tag = ua['family']
        if version:
            tag += ' ' + version

        return tag

register(OsPlugin)


class DevicePlugin(UserAgentPlugin):
    """
    Automatically adds the 'device' tag from events containing interface data
    from ``sentry.interfaces.Http``.
    """
    slug = 'device'
    title = _('Auto Tag: Device')
    tag = 'device'
    tag_label = _('Device')

    def get_tag_from_ua(self, ua):
        return ua['device']['family']

register(DevicePlugin)
