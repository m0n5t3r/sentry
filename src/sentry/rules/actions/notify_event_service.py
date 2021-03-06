"""
sentry.rules.actions.notify_event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

from django import forms

from sentry.plugins import plugins
from sentry.rules.actions.base import EventAction


class NotifyEventServiceForm(forms.Form):
    service = forms.ChoiceField(choices=())

    def __init__(self, *args, **kwargs):
        service_choices = [
            (plugin.slug, plugin.get_title())
            for plugin in kwargs.pop('plugins')
        ]

        super(NotifyEventServiceForm, self).__init__(*args, **kwargs)

        self.fields['service'].choices = service_choices
        self.fields['service'].widget.choices = self.fields['service'].choices


class NotifyEventServiceAction(EventAction):
    form_cls = NotifyEventServiceForm
    label = 'Send a notification via {service}'

    def after(self, event, state):
        service = self.get_option('service')

        if not service:
            return

        plugin = plugins.get(service)
        if not plugin.is_enabled(self.project):
            return

        group = event.group

        if not plugin.should_notify(group=group, event=event):
            return

        plugin.notify_users(group=group, event=event)

    def get_plugins(self):
        from sentry.plugins.bases.notify import NotificationPlugin

        results = []
        for plugin in plugins.for_project(self.project):
            if not isinstance(plugin, NotificationPlugin):
                continue
            results.append(plugin)
        return results

    def get_form_instance(self):
        return self.form_cls(
            self.data,
            plugins=self.get_plugins(),
        )
