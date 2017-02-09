# -*- coding: utf-8 -*-

from django.conf.urls import url
from microb.views import MachinesView, ServerView


urlpatterns = [
    url(r'^(?P<server>[-_\w]+)/$', ServerView.as_view(), name="microb-server"),
    url(r'^', MachinesView.as_view(), name="microb-index"),
    ]