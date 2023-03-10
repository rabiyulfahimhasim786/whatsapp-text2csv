from django.shortcuts import render, redirect
from django.http import HttpResponse
import regex
import pandas as pd
import numpy as np
import emoji
from collections import Counter
import matplotlib.pyplot as plt
#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from .models import whatsapp
from .forms import WhatsappForm


def date_time(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -'
    result = regex.match(pattern, s)
    if result:
        return True
    return False

def find_author(s):
    s = s.split(":")
    if len(s)==2:
        return True
    else:
        return False

def getDatapoint(line):
    splitline = line.split(' - ')
    dateTime = splitline[0]
    date, time = dateTime.split(", ")
    message = " ".join(splitline[1:])
    if find_author(message):
        splitmessage = message.split(": ")
        author = splitmessage[0]
        message = " ".join(splitmessage[1:])
    else:
        author= None
    return date, time, author, message
dot='./media/'
def index(requests):
    documents = whatsapp.objects.all()
    for obj in documents:
        baseurls = obj.chat
    print(baseurls)
    data = []
    #conversation = 'whatsapp-chat-data.txt'
    conversation = dot + str(baseurls)
    print(conversation)
    with open(conversation, encoding="utf-8") as fp:
        fp.readline()
        messageBuffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_time(line):
                if len(messageBuffer) > 0:
                    data.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                    date, time, author, message = getDatapoint(line)
                    messageBuffer.append(message)
                else:
                    messageBuffer.append(line)
    df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.to_csv('./media/data.csv', index = False)
    return HttpResponse('halloo world')


def upload_txt(request):
    if request.method == 'POST':
        form = WhatsappForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return redirect('index')
            documents = whatsapp.objects.all()
            for obj in documents:
                baseurls = obj.chat
            print(baseurls)
            data = []
            #conversation = 'whatsapp-chat-data.txt'
            conversation = dot + str(baseurls)
            print(conversation)
            with open(conversation, encoding="utf-8") as fp:
                fp.readline()
                messageBuffer = []
                date, time, author = None, None, None
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    line = line.strip()
                    if date_time(line):
                        if len(messageBuffer) > 0:
                            data.append([date, time, author, ' '.join(messageBuffer)])
                            messageBuffer.clear()
                            date, time, author, message = getDatapoint(line)
                            messageBuffer.append(message)
                        else:
                            messageBuffer.append(line)
            df = pd.DataFrame(data, columns=["Date", 'Time', 'Author', 'Message'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.to_csv(dot+'media/data.csv', index = False)
            return render(request, 'form_upload.html', {})
    else:
        form = WhatsappForm()
        documents = whatsapp.objects.all()
    return render(request, 'form_upload.html', {
        'form': form
    })