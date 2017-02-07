# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from djR.r_producers import R
from microb.models import Page, Site
from microb.conf import DB, TABLE

"""
WORK IN PROGRESS
"""


def add_page(site, db_page, page):
    Page.objects.create(
                        url = db_page["url"], 
                        title = db_page["title"],
                        content = db_page["fields"]["content"],
                        site = site,
                        
                        )
    
def synchronize_site(site, domain):
    if site is None:
        Site.objects.create(domain=domain, title=domain)
        print "Site "+domain+" created in local database"
    pages = Page.objects.filter(site=site)
    filters = {"domain": domain}
    in_db_pages = R.get_filtered(DB, TABLE, filters)
    urls = []
    if pages is not None:
        for page in pages:
            urls.append(page.url)
    print str(urls)
    for db_page in in_db_pages:
        url = db_page["uri"]
        if url in urls:
            update_page(site, db_page, pages.filter(url=url))
        else:
            add_page(db_page, pages.filter(url=url))
    return

class Command(BaseCommand):
    help = 'Synchronize Microb db'
    
    def add_arguments(self, parser):
        parser.add_argument('site', nargs='+', type=str)

    def handle(self, *args, **options):
        print "Synchronizing Microb db ..."
        domain = options["site"][0]
        try:
            site = Site.objects.get(domain=domain)
        except ObjectDoesNotExist:
            site = None
            print "Site "+domain+" not found in local db"
        synchronize_site(site, domain)
        return
