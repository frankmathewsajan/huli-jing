from django.contrib import admin

# Register your models here.
from .models import DailySchedule, Task
admin.site.register(DailySchedule)
admin.site.register(Task)