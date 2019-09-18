from django.urls import path
from . import views
from django.views.decorators.cache import never_cache

urlpatterns = [
    path('', never_cache(views.waiting), name='waiting'),
    path('signup', never_cache(views.signup), name='signup'),
    path('timer/', views.timer, name='timer'),
    path('logout', views.user_logout, name='logout'),
    path('leaderboard', views.leader, name='leader'),
    path('instructions', never_cache(views.instructions), name='instructions'),
    path('checkUsername', views.check_username, name='check_username'),
    path('loadBuffer', views.loadBuffer, name='loadBuffer'),
    path('user/allque', views.questionHub, name='questionHub'),
    path('user/<username>/<int:qn>', views.codeSave, name='codeSave'),
    path('user/<username>/<int:qn>/submission', views.submission, name='submission'),
]
