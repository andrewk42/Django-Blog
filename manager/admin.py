from manager.models import Settings, Visit
from django.contrib import admin

'''class PostAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields': ['category', 'publish_date']}),
        ("Content", {'fields': ['title', 'body']}),
    ]
    list_display = ('__unicode__', 'category', 'urlname')
    list_filter = ['category', 'publish_date', 'modified_date', 'create_date']
    search_fields = ['title', 'body']
    date_hierarchy = 'create_date'''

admin.site.register(Settings)
admin.site.register(Visit)
