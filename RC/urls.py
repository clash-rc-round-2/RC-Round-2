from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),
    path('timer/', views.timer, name='timer'),
    path('logout', views.user_logout, name='logout'),
    path('leaderboard', views.leader, name='leader'),
    path('instructions/', views.instructions, name='instructions'),
#    path('loadBuffer', views.loadBuffer, name='loadBuffer'),
    path('user/allque', views.questionHub, name='questionHub'),
    path('user/<username>/<int:qn>', views.codeSave, name='codeSave'),
    path('user/<username>/submission', views.submission, name='submission'),
    path('user/<username>/<int:qn>/<int:att>/testCases', views.runCode, name='runCode'),

]
