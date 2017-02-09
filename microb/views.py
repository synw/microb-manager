# -*- coding: utf-8 -*-

import json
from django.http.response import Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from microb.models import Machine, HttpServer
from instant.utils import signed_response
from instant.conf import USERS_CHANNELS, STAFF_CHANNELS, SUPERUSER_CHANNELS


class MachinesView(TemplateView):
    template_name = "microb/index.html"
    
    def get_context_data(self, **kwargs):
        context = super(MachinesView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser is False:
            raise Http404
        machines = Machine.objects.all().prefetch_related("servers")
        context["machines"] = machines
        return context
    
    
class ServerView(TemplateView):
    template_name = "microb/server.html"
    
    def get_context_data(self, **kwargs):
        context = super(ServerView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser is False:
            raise Http404
        server = get_object_or_404(HttpServer, domain=kwargs["server"])
        context["server"] = server
        return context
    

@csrf_exempt
def microb_auth(request):
    if not request.is_ajax() or not request.method == "POST":
        raise Http404
    data = json.loads(request.body.decode("utf-8"))
    channels = data["channels"]
    client = data['client']
    response = {}
    for channel in channels:
        signature = None
        if channel in USERS_CHANNELS:
            if request.user.is_authenticated():
                signature = signed_response(channel, client)
        if channel in STAFF_CHANNELS or channel == "$dev_hits":
            if request.user.is_staff:
                signature = signed_response(channel, client)
        if channel in SUPERUSER_CHANNELS:
            if request.user.is_superuser:
                signature = signed_response(channel, client)
        if signature is not None:
            response[channel] = signature
        else:
            response[channel] = {"status":"403"}
    return JsonResponse(response)