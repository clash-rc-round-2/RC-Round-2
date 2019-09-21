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
    path('user/<username>/<int:qn>/<int:att>/viewSub', views.view_sub, name='view_sub'),
    path('user/allque', never_cache(views.questionHub), name='questionHub'),
    path('user/<username>/<int:qn>', views.codeSave, name='codeSave'),
    path('emerlogin/', views.emergency_login),
    path('user/<username>/<int:qn>/submission', never_cache(views.submission), name='submission'),
    url(r'^(?P<garbage>.*)/$', views.garbage, name='redirect'),
    path('getOutput', views.getOutput, name='getOutput')
    # path('user/<username>/<int:qn>/<int:att>/testCases', views.runCode, name='runCode'),
]
