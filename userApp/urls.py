from django.urls import path
from . import views
from django.conf.urls import url
from django.views.decorators.cache import never_cache

urlpatterns = [
    path('', views.waiting, name='waiting'),
    path('signup', views.signup, name='signup'),
    path('timer/', views.timer, name='timer'),
    path('logout', views.user_logout, name='logout'),
    path('leaderboard', never_cache(views.leader), name='leader'),
    path('instructions', views.instructions, name='instructions'),
    path('checkUsername', views.check_username, name='check_username'),
    path('loadBuffer', views.loadBuffer, name='loadBuffer'),
    path('submissions/<int:qno>/<int:_id>/', views.view_sub, name='view_sub'),
    path('user/allque', never_cache(views.questionHub), name='questionHub'),
    path('user/<int:qn>', views.codeSave, name='codeSave'),
    path('emerlogin/', views.emergency_login),
    path('user/<int:qn>/submission', never_cache(views.submission), name='submission'),
    url(r'^(?P<garbage>.*)/$', views.garbage, name='redirect'),
    path('getOutput', views.getOutput, name='getOutput')
]
