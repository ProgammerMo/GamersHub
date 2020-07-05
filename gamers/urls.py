from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("logout", views.logoutpage, name="logout"),
    path("search/game/manage/<str:game>", views.search_games_manage, name="search_games"),
    path("add/game/<int:game>", views.add_game, name="add_game"),
    path("search/players/<str:game>/<int:start>/<int:end>", views.search_players_game, name="search_players"),
    path("user/manage/<int:user>/<str:request_type>", views.users_manage, name="add_cancel_friend"),
    path("socket/<str:type>/<str:channel>", views.chat_channel, name="chat_channel"),
    path("message/<int:user>", csrf_exempt(views.chat_message) , name="chat_message"),
    path("my_frequests", views.my_frequests, name="my_frequests"),
    path("my_friendlist", views.my_friendlist, name="my_friendlist"),
    path("updatep",  csrf_exempt(views.update_profile), name="logout"),  
]