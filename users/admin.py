from django.contrib import admin

# Register your models here.
from .models import User, Goal, Commitment, UserPattern
admin.site.register(User)
admin.site.register(UserPattern)
admin.site.register(Goal)
admin.site.register(Commitment)
