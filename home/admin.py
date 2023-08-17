from django.contrib import admin

from home.views import dataModel

# Register your models here.


class dataAdmin(admin.ModelAdmin):
    list_display = (['Name'])


admin.site.register(dataModel, dataAdmin)
