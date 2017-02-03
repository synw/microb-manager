# -*- coding: utf-8 -*-

import json
import rethinkdb as r
from django.core.management import call_command
from django.core import serializers
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from mptt.models import TreeForeignKey, MPTTModel
from djR.r_producers import R
from microb.conf import USER_MODEL, DB, TABLE


def content_file_name(instance, filename):
    return '/'.join([instance.page.site.domain, "img", filename])

class Seo(models.Model):
    seo_description = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(u'SEO: description'), help_text=_(u'Short description of the page content'))
    seo_keywords = models.CharField(max_length=120, null=True, blank=True, verbose_name=_(u'SEO: keywords'), help_text=_(u'List of keywords separated by commas'))

    class Meta:
        abstract = True
        verbose_name=_(u'SEO')


class Site(models.Model):
    title = models.CharField(_(u'Title'), max_length=200)
    domain = models.CharField(_(u'Domain'), max_length=200)
    
    def __unicode__(self):
        return unicode(self.title)


class Page(MPTTModel, Seo):
    url = models.CharField(_(u'Url'), max_length=180, db_index=True)
    title = models.CharField(_(u'Title'), max_length=200)
    content = models.TextField(_(u'Content'), blank=True)
    site = models.ForeignKey(Site, verbose_name=_(u"Site"))
    parent = TreeForeignKey('self', null=True, blank=True, related_name=u'children', verbose_name=_(u'Parent page'))
    edited = models.DateTimeField(editable=False, null=True, auto_now=True, verbose_name=_(u'Edited'))
    created = models.DateTimeField(editable=False, null=True, auto_now_add=True, verbose_name=_(u'Created'))
    editor = models.ForeignKey(USER_MODEL, editable = False, related_name='+', null=True, on_delete=models.SET_NULL, verbose_name=_(u'Edited by'))   
    published = models.BooleanField(default=True, verbose_name=_(u'Published'))
    extra_data = JSONField(blank=True, verbose_name=_(u'Extra data'))
    
    class Meta:
        verbose_name = _(u'Page')
        verbose_name_plural = _(u'Page')
        ordering = ['url']
        
        
    def get_absolute_url(self):
        return self.url
    
    def __unicode__(self):
        return unicode(self.title)
    
    def document_exists(self):
        domain = self.site.domain
        q = r.db(DB).table(TABLE).get_all([self.url, domain], index="key").count()
        #existing_documents = order_documents(R.run_query(q))
        #print modelname+" | "+str(pk)+" _> "+str(existing_documents)
        existing_documents = R.run_query(q)
        json_document_exists = False
        if existing_documents > 0:
            json_document_exists = True
        return json_document_exists
    
    def serialize(self):
        domain = self.site.domain
        data = json.loads(serializers.serialize("json", [self])[1:-1])
        data["domain"] = domain
        data["uri"] = self.url
        if self.editor is not None:
            data[u"editor"] = self.editor.username
        if self.parent is not None:
            data[u"parent"] = self.parent.url
        return data
     
    def delete(self, *args, **kwargs):
        super(Page, self).delete(*args, **kwargs)
        return
    
    def mirror(self, data):
        #print 'Exists: '+str(self.document_exists())
        if self.document_exists() is True:
            filters = (r.row['domain'] == self.site.domain) & (r.row['uri'] == self.url)
            res = R.update(DB, TABLE, data, filters)
        else:
            res = R.write(DB, TABLE, data)
        return res
    
    def update_routes(self):
        call_command('microb_routes', verbosity=0)
        return

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)
        data = self.serialize()
        self.mirror(data)
        self.update_routes()
        #print str(json.dumps(data, indent=4))
        return


class Image(models.Model):
    image = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    page = models.ForeignKey(Page, verbose_name=_(u"Page"))
