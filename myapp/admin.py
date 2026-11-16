from django.contrib import admin

from myapp.models import StockInfo


@admin.register(StockInfo)
class StockInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "industry", "overall_grade", "overall_grade_num", "last_update")
    list_filter = ("overall_grade", "sector")
    search_fields = ("name", "company_name", "industry")
    ordering = ("-overall_grade_num",)
    exclude = ("prices", "dates")  # thousands of numbers; too big for a form
