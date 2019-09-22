import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rc.settings")

django.setup()

from userApp.models import Question

QUESTIONS = 8

os.system("mkdir data/usersCode")
os.system("python3 manage.py makemigrations userApp")
os.system("python3 manage.py migrate")

path = 'description/'

# for filename in os.listdir(path):
#     file = open(path + filename, 'r')
#     content = file.read()
#     print(str(content))
#     question = Question(question=content, titleQue=filename)
#     question.save()
#     file.close()
