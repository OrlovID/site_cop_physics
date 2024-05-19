from django.contrib import admin

# Register your models here.

from .models import PhysThemes, PhysTasks


class PhysTasksAdmin(admin.ModelAdmin):
    list_display = ('name', 'descr_shorter', 'theme')
    list_filter = ('theme', "trust")


admin.site.register(PhysThemes)
admin.site.register(PhysTasks, PhysTasksAdmin)
