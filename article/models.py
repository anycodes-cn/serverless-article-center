from django.db import models
from mdeditor.fields import MDTextField

# Create your models here.

class ArticleModel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="标题")
    create_time = models.DateTimeField(null=True, blank=True, auto_created=True, auto_now_add=True, verbose_name='创建时间')
    description = models.TextField(null=True, blank=True, verbose_name="描述")
    content = MDTextField()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'