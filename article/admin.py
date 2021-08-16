from django.contrib import admin
from article.models import *
# Register your models here.

admin.site.site_header = '文章中心'
admin.site.site_title = '文章中心'


class ArticleModelAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('id', 'title', 'create_time',)
    list_display_links = ('id', 'title',)


admin.site.register(ArticleModel, ArticleModelAdmin)