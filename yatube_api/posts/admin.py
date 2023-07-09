from django.contrib import admin

from .models import Group, Post, Follow, Comment

admin.site.register([Group, Post, Follow, Comment])
