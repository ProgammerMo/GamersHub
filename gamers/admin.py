from django.contrib import admin
from .models import Gamer, Platform, Game, Category, Gamer_ID, Friend, Friend_Request, Chat, Message

# Register your models here.

admin.site.register(Gamer)
admin.site.register(Platform)
admin.site.register(Game)
admin.site.register(Category)
admin.site.register(Gamer_ID)
admin.site.register(Friend)
admin.site.register(Friend_Request)
admin.site.register(Chat)
admin.site.register(Message)
