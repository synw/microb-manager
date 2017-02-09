# -*- coding: utf-8 -*-

import json
import rethinkdb as r
from django.core import serializers
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from mptt.models import TreeForeignKey, MPTTModel
from djR.r_producers import R
from microb.conf import USER_MODEL


def content_file_name(instance, filename):
    return '/'.join([instance.page.site.domain, "img", filename])

class Seo(models.Model):
    seo_description = models.CharField(max_length=256, null=True, blank=True, verbose_name=_(u'SEO: description'), help_text=_(u'Short description of the page content'))
    seo_keywords = models.CharField(max_length=120, null=True, blank=True, verbose_name=_(u'SEO: keywords'), help_text=_(u'List of keywords separated by commas'))

    class Meta:
        abstract = True
        verbose_name=_(u'SEO')


class Machine(models.Model):
    name = models.SlugField(unique=True, verbose_name=_(u'Name'), max_length=200)
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_(u'Ip adress'))
    
    def __unicode__(self):
        return unicode(self.name)+" - "+str(self.ip)


class HttpServer(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    domain = models.CharField(_(u'Domain'), max_length=200)
    machine = models.ForeignKey(Machine, verbose_name=_(u"Machine"))
    port = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_(u"Port"))
    
    def __unicode__(self):
        return unicode(self.name)
   

class SiteTemplate(models.Model):
    content = models.TextField(_(u'Content'), blank=True)
    server = models.ForeignKey(HttpServer, verbose_name=_(u"Site"))
    edited = models.DateTimeField(editable=False, null=True, auto_now=True, verbose_name=_(u'Edited'))
    created = models.DateTimeField(editable=False, null=True, auto_now_add=True, verbose_name=_(u'Created'))
    editor = models.ForeignKey(USER_MODEL, editable = False, related_name='+', null=True, on_delete=models.SET_NULL, verbose_name=_(u'Edited by'))   
    
    class Meta:
        verbose_name = _(u'Site template')
        verbose_name_plural = _(u'Site templates')

    def __unicode__(self):
        return unicode(self.server.title)
    
    def save(self, *args, **kwargs):
        super(SiteTemplate, self).save(*args, **kwargs)
        # save template to Microb server
        filepath=settings.BASE_DIR+"/microb/servers/"+self.server.domain+"/templates/view.html"
        #~ write the file
        filex = open(filepath, "w")
        filex.write(self.content.encode('utf-8'))
        filex.close()
        # send command to the Microb server to reparse the templates
        data = {"Name": "reparse_templates", "Reason": "Template edit"}
        R.write(self.server.domain, "commands", data)
        return

    
class SiteCss(models.Model):
    content = models.TextField(_(u'Content'), blank=True)
    server = models.ForeignKey(HttpServer, verbose_name=_(u"Site"))
    edited = models.DateTimeField(editable=False, null=True, auto_now=True, verbose_name=_(u'Edited'))
    created = models.DateTimeField(editable=False, null=True, auto_now_add=True, verbose_name=_(u'Created'))
    editor = models.ForeignKey(USER_MODEL, editable = False, related_name='+', null=True, on_delete=models.SET_NULL, verbose_name=_(u'Edited by'))   
    
    class Meta:
        verbose_name = _(u'Site css')
        verbose_name_plural = _(u'Site css')

    def __unicode__(self):
        return unicode(self.server.title)
    
    def save(self, *args, **kwargs):
        super(SiteCss, self).save(*args, **kwargs)
        # save template to Microb server
        filepath=settings.BASE_DIR+"/microb/servers/"+self.server.domain+"/static/css/screen.css"
        #~ write the file
        filex = open(filepath, "w")
        filex.write(self.content.encode('utf-8'))
        filex.close()
        return


class Page(MPTTModel, Seo):
    url = models.CharField(_(u'Url'), max_length=180, db_index=True)
    title = models.CharField(_(u'Title'), max_length=200)
    content = models.TextField(_(u'Content'), blank=True)
    server = models.ForeignKey(HttpServer, verbose_name=_(u"Site"))
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
        domain = self.server.domain
        q = r.db(self.server.domain).table("pages").get_all([self.url, domain], index="key").count()
        #existing_documents = order_documents(R.run_query(q))
        #print modelname+" | "+str(pk)+" _> "+str(existing_documents)
        existing_documents = R.run_query(q)
        json_document_exists = False
        if existing_documents > 0:
            json_document_exists = True
        return json_document_exists
    
    def serialize(self):
        domain = self.server.domain
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
        filters = (r.row['domain'] == self.server.domain) & (r.row['uri'] == self.url)
        res = R.delete_filtered(self.server.domain, "pages", filters)
        return res
    
    def mirror(self, data):
        #print 'Exists: '+str(self.document_exists())
        if self.document_exists() is True:
            filters = (r.row['domain'] == self.server.domain) & (r.row['uri'] == self.url)
            res = R.update(self.server.domain, "pages", data, filters)
        else:
            res = R.write(self.server.domain, "pages", data)
        return res

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)
        data = self.serialize()
        self.mirror(data)
        #print str(json.dumps(data, indent=4))
        return


class ImageCss(models.Model):
    image = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    page = models.ForeignKey(SiteCss, verbose_name=_(u"Css"))
    
    
class ImageTemplate(models.Model):
    image = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    page = models.ForeignKey(SiteTemplate, verbose_name=_(u"Template"))


class Image(models.Model):
    image = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    page = models.ForeignKey(Page, verbose_name=_(u"Page"))
