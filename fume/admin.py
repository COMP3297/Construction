from django.contrib import admin

# Register your models here.

from .models import Game , Tag, Purchase, Cart, GameImage  , Platform,Reward


admin.site.register(Game)
admin.site.register(Tag)
admin.site.register(Purchase)
admin.site.register(Cart)
admin.site.register(GameImage)
admin.site.register(Platform)
admin.site.register(Reward)
