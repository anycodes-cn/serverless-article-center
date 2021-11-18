# 基于Serverless架构的社区文章管理小工具

## 前言

我是一个非常喜欢写一些东西的人，写完了一些文章什么的，我会考虑把他们发布到一些平台，例如微信公众号，例如知乎，例如我的博客等。

但是实际的情况却有一些尴尬：

1. 不同平台所能接受的格式内容是不同的，例如我的博客支持Markdown，但是知乎，微信公众号，貌似只支持富文本的复制粘贴，所以这就涉及到我要在不同平台之间切换不同的格式；
2. 有的时候，图片真的是一个坑爹的事情，我在Github上面截图粘贴了很多图片，复制到公众号，知乎等平台之后，发现所有的图片还需要重新截图粘贴（可能是网络问题，也可能是跨域等其他问题，反正图片是拿不回来）

所以我就一直在想，是否可以有一个非常简单的项目，他只需要帮我做几个事情就可以：

1. 我可以在这个上面写文章，写博客，并且可以用Markdown的语法来写
2. 写完了之后可以生成富文本的样子，便于我可以快速复制和粘贴
3. 我可以直接截图粘贴图片，这些图片可以在不同平台直接使用

## 项目开发

我通过Python的Django框架，快速搭建起来一个架子。并且根据资料发现，我可以使用`django-mdeditor`来做Markdown的编写、预览；

所以，我将`django-mdeditor`安装好之后，我编写`models.py`：

```python
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
```

此时，我的文章正文（`content`字段），就可以使用`django-mdeditor`的内容了。

完成之后，我在`admin.py`中配置一下字段等：

```python
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
```

完成之后，可能还需要配置一下数据库信息，然后同步数据库，常见超级管理员等。完成之后，我们可以打开`/admin`：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105100097_20210816091142893266.png)

登陆之后可以看到：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105153160_20210816091233283290.png)

此时，我们可以新建一个文章：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105208694_20210816091328804808.png)

可以看到整个效果还是非常棒的。

### 魔改编辑器

但是，这里有一个问题，那就是图片不能粘贴。所以，我们要对刚刚安装的`django-mdeditor`进行魔改，此处为了便于修改之后在其他平台生效，我们将这个模块安装到当前项目：`pip3 install -t . django-mdeditor`

此时对html文件进行修改：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105501904_20210816091822415063.png)

在第91行添加：`initPasteDragImg(this); //必须`

然后，在这个`script`标签中，增加：

```javascript
function initPasteDragImg(Editor){
    var doc = document.getElementById(Editor.id)
    doc.addEventListener('paste', function (event) {
        var items = (event.clipboardData || window.clipboardData).items;
        var file = null;
        if (items && items.length) {
            // 搜索剪切板items
            for (var i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    file = items[i].getAsFile();
                    break;
                }
            }
        } else {
            console.log("当前浏览器不支持");
            return;
        }
        if (!file) {
            console.log("粘贴内容非图片");
            return;
        }
        uploadImg(file,Editor);
    });
    var dashboard = document.getElementById(Editor.id)
    dashboard.addEventListener("dragover", function (e) {
        e.preventDefault()
        e.stopPropagation()
    })
    dashboard.addEventListener("dragenter", function (e) {
        e.preventDefault()
        e.stopPropagation()
    })
    dashboard.addEventListener("drop", function (e) {
        e.preventDefault()
        e.stopPropagation()
     var files = this.files || e.dataTransfer.files;
     uploadImg(files[0],Editor);
     })
}
function uploadImg(file,Editor){
    var formData = new FormData();
    var fileName=new Date().getTime()+"."+file.name.split(".").pop();
    formData.append('editormd-image-file', file, fileName);
    formData.append('content', '');
    $.ajax({
        url: Editor.settings.imageUploadURL,
        type: 'post',
        data: formData,
        processData: false,
        contentType: false,
        dataType: 'json',
        success: function (msg) {
            var success=msg['success'];
            if(success==1){
                var url=msg["url"];
                if(/\.(png|jpg|jpeg|gif|bmp|ico)$/.test(url)){
                    Editor.insertValue("![图片alt]("+msg["url"]+" ''图片title'')");
                }else{
                    Editor.insertValue("[下载附件]("+msg["url"]+")");
                }
            }else{
                console.log(msg);
                alert("上传失败");
            }
        }
    });
}
```

完成之后，还有一个问题：我们粘贴之后是会上传到当前项目下，但是在Serverless架构下，进行图片持久化是不能放在当前项目的，毕竟实例会被释放掉，所以这里还需要对存储位置进行改变：


![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105706467_20210816092147104634.png)

```python
import oss2
bucketName = os.environ.get('oss_BUCKET', '')
endpoint = os.environ.get('oss_ENDPOINT', '')
auth = oss2.Auth(os.environ.get('aliyun_KeyId', ''), os.environ.get('aliyun_KeySecret', ''))
bucket = oss2.Bucket(auth, endpoint, bucketName)
```

完成之后，还需要对文件存储部分进行额外处理：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105778870_20210816092259339538.png)

1. 注释掉红色的：不需要检查本地路径和写入到本地
2. 增加蓝色的部分：将图片上传到对象存储`bucket.put_object(file_full_name, upload_image.chunks())`
3. 修改黄色的部分：将结果返回给前端：` 'url': 'https://%s.%s/%s'%(bucketName, endpoint, file_full_name)`

完成之后，我们再重新运行一下项目，我们可以看到，是可以直接实现图片粘贴的，粘贴后的效果：

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629105920067_20210816092520381872.png)

## 部署到线上

为了和函数计算做结合，只需要增加两个文件就可以：

文件1，函数入口，新建`index.py`：

```python
from articleCenter.wsgi import application
```

文件2，资源描述文件，新建`s.yaml`：

```yaml
edition: 1.0.0          #  命令行YAML规范版本，遵循语义化版本（Semantic Versioning）规范
name: serverless-article       #  项目名称
access: "default"  #  秘钥别名

services:
  article: #  服务名称
    component: devsapp/fc  # 组件名称
    props: #  组件的属性值
      region: cn-hangzhou
      service:
        name: serverless-article
        internetAccess: true
      function:
        name: server
        runtime: python3
        codeUri: ./
        handler: index.application
        memorySize: 128
        timeout: 60
        environmentVariables:
          aliyun_KeyId: ''
          aliyun_KeySecret: ''
          db_HOST: ''
          db_NAME: ''
          db_PASSWORD: ''
          db_PORT: ''
          db_USER: ''
          oss_BUCKET: ''
          oss_ENDPOINT: ''
      triggers:
        - name: httpTrigger
          type: http
          config:
            authType: anonymous
            methods:
              - GET
              - POST
              - PUT
              - DELETE
      customDomains:
        - domainName: auto
          protocol: HTTP
          routeConfigs:
            - path: /*
              methods:
                - GET
```

## 快速使用

我将该项目放在了Github：https://github.com/anycodes-cn/serverless-article-center

![图片alt](https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1629106074688_20210816092755070981.png)

大家只需要Clone这个项目，然后编辑`s.yaml`，添加数据库信息，对象存储信息。

然后进行项目处理和部署处理。

### 项目处理

1. 在项目中执行数据库同步`makemigrations`和`migrate`
2. 创建超级用户，同样是`manage.py`的指令：`createsuperuser`
3. 静态文件处理：`collectstatic`

### 部署处理

1. 执行`s build --use-docker`进行构建
2. 执行`s deploy`进行项目部署

## 总结

一个非常简单的小工具，希望可以帮助和帮助更多人快速编写一些文章，进行保存和多平台的发布

## todo

1. 自动发布到不同的平台


