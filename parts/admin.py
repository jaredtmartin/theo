from django.contrib import admin
from parts.models import Category, Setting, CounselPoint, Publisher, Part, Assignment, Congregation, Meeting
class PartAdmin(admin.ModelAdmin):
  list_display = ('theme','material','order', 'date','category')
class AssignmentAdmin(admin.ModelAdmin):
  list_display = ('title','date','publisher','congregation','category')
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name','meeting')
admin.site.register(Category, CategoryAdmin)
admin.site.register(Setting)
admin.site.register(CounselPoint)
admin.site.register(Publisher)
admin.site.register(Part, PartAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Congregation)
admin.site.register(Meeting)