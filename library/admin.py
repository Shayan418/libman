from django.contrib import admin
from .models import *
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'book', 'timeCreated')

admin.site.register(User)
admin.site.register(Books)
admin.site.register(record, CommentAdmin)