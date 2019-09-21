import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rc.settings")

django.setup()

from userApp.models import Question

QUESTIONS = 6

path = os.environ['HOME'] + '/Projects/Credenz/ClashRound2/queDescrip/'

os.system("python3 manage.py makemigrations userApp")
os.system("python3 manage.py migrate")

for filename in os.listdir(path):
    file = open(path + filename, 'r')
    content = file.read()
    print(str(content))
    question = Question(question=content, titleQue=filename)
    question.save()
    file.close()
