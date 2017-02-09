# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from djR.r_producers import R
from microb.models import Page, HttpServer


def check_parent(db_page, page, save=False):
    if db_page["fields"]["parent"] is not None:
        parent_page, created = Page.objects.get_or_create(url=db_page["parent"])
        page.parent = parent_page
        if save is True:
            page.save()
    return

def add_page(db_page, server):
    page = Page.objects.create(
                        server = server,
                        url = db_page["uri"], 
                        title = db_page["fields"]["title"],
                        content = db_page["fields"]["content"],
                        extra_data = db_page["fields"]["extra_data"],
                        )
    check_parent(db_page, page, True)
    return
        

def update_page(db_page, page):
    page.domain = db_page["domain"]
    page.url = db_page["uri"]
    page.title = db_page["fields"]["title"]
    page.content = db_page["fields"]["content"]
    page.extra_data = db_page["fields"]["extra_data"]
    check_parent(db_page, page)
    page.save()
    return

def synchronize_server(server, domain):
    updated = 0
    created = 0
    # create a HttpServer object if not present
    if server is None:
        server = HttpServer.objects.create(domain=domain, name=domain)
        print "Server "+domain+" created in local database"
    pages = Page.objects.filter(server=server)
    # query main db
    filters = {"domain": domain}
    in_db_pages = R.get_filtered(domain, "pages", filters)
    urls = []
    if pages is not None:
        for page in pages:
            urls.append(page.url)
    for db_page in in_db_pages:
        url = db_page["uri"]
        if url in urls:
            page = pages.filter(url=url)[0]
            update_page(db_page, page)
            print "Page "+page.url+" updated"
            updated += 1
        else:
            add_page(db_page, server)
            print "Page "+page.url+" added"
            created += 1
    return updated, created

class Command(BaseCommand):
    help = 'Synchronize Microb Manager local db for server'
    
    def add_arguments(self, parser):
        parser.add_argument('domain', nargs='+', type=str)

    def handle(self, *args, **options):
        domain = options["domain"][0]
        print "Synchronizing Microb Manager local db for server "+domain+"..."
        try:
            server = HttpServer.objects.get(domain=domain)
        except ObjectDoesNotExist:
            server = None
            print "Site "+domain+" not found in local db"
        updated, created = synchronize_server(server, domain)
        print str(updated)+" pages updated"
        print str(created)+" pages created"
        return
