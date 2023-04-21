from django.contrib import admin

from home.models import dataModel

# Register your models here.


class dataAdmin(admin.ModelAdmin):
    list_display = (['Name'])


admin.site.register(dataModel, dataAdmin)
