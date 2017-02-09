# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from microb.models import Machine, HttpServer, Page, Image, SiteTemplate, SiteCss, ImageTemplate, ImageCss
from microb.forms import PageAdminForm, SiteTemplateForm, SiteCssForm
from microb.conf import USE_REVERSION


class HttpServerInline(admin.TabularInline):
    model = HttpServer
    fields = ['name', 'domain', "port"]
    extra = 0

class ImageInline(admin.TabularInline):
    model = Image
    fields = ['image']
    extra = 0
    

class ImageTemplateInline(admin.TabularInline):
    model = ImageTemplate
    fields = ['image']
    extra = 0


class ImageCssInline(admin.TabularInline):
    model = ImageCss
    fields = ['image']
    extra = 0


if USE_REVERSION:
    from reversion.admin import VersionAdmin
admin_class=admin.ModelAdmin
if USE_REVERSION:
    admin_class=VersionAdmin
@admin.register(Page)
class PageAdmin(MPTTModelAdmin, admin_class):
    form = PageAdminForm
    date_hierarchy = 'edited'
    search_fields = ['title','url','editor__username']
    list_display = ['url','title', 'published','edited','editor', 'server']
    list_select_related = ['editor']
    list_display_links = ['title','url']
    list_filter = ['server', 'created','edited','published']
    list_select_related = ['editor', 'server']
    mptt_level_indent = 25
    save_on_top = True
    inlines = [ImageInline]
    
    def get_fieldsets(self, request, obj=None):
        super(PageAdmin, self).get_fieldsets(request, obj)
        base_fields = (('url', 'title'),('server', 'parent'), 'published')
        fieldsets = (
            (None, {
                'fields': ('content',)
            }),
            (None, {
                'fields': base_fields,
            }),
            (_(u'SEO'), {
                'classes': ('collapse',),
                'fields': ('seo_keywords','seo_description')
            }),
            (_(u'Extra data'), {
                'classes': ('collapse',),
                'fields': ('extra_data',)
            }),
        )
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        obj.save()
        return


@admin.register(SiteTemplate)
class SitesTemplatesAdmin(VersionAdmin):
    date_hierarchy = 'edited'
    save_on_top = True
    form = SiteTemplateForm
    inlines = [ImageTemplateInline]

    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        obj.save()
        return


@admin.register(SiteCss)
class SitesCssAdmin(VersionAdmin):
    date_hierarchy = 'edited'
    save_on_top = True
    form = SiteCssForm
    inlines = [ImageCssInline]

    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        obj.save()
        return


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    inlines = [HttpServerInline]


@admin.register(HttpServer)
class HttpServerAdmin(admin.ModelAdmin):
    pass
