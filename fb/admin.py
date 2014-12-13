from django.contrib import admin

from fb.models import UserPost, UserProfile, Image, Album


admin.site.register(UserPost)
admin.site.register(UserProfile)
admin.site.register(Image)
admin.site.register(Album)


