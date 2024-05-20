from django.contrib import admin

# Register your models here.

from .models import PhysThemes, PhysTasks


class PhysTasksAdmin(admin.ModelAdmin):
    list_display = ('name', 'descr_shorter', 'display_theme')
    list_filter = ('theme__theme', "trust")


class PhysThemesAdmin(admin.ModelAdmin):
    pass


admin.site.register(PhysThemes, PhysThemesAdmin)
admin.site.register(PhysTasks, PhysTasksAdmin)
