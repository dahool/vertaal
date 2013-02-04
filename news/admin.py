from django.contrib import admin
from news.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'expires']
    readonly_fields = ['author','created']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        obj.save()
    
admin.site.register(Article, ArticleAdmin)