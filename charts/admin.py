from django.contrib import admin
from starchart.charts.models import Chart, CheckIn

class CheckInAdmin(admin.ModelAdmin):
    display = ('when', 'number')
    ordering = ('-when',)

class ChartAdmin(admin.ModelAdmin):
    search_fields = ('title',)

admin.site.register(Chart, ChartAdmin)
admin.site.register(CheckIn, CheckInAdmin)
