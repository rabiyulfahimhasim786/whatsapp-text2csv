from django.shortcuts import render, redirect
from django.http import HttpResponse
import regex
import pandas as pd
import numpy as np
import emoji
import csv
import json
from collections import Counter
from django.shortcuts import get_object_or_404
import matplotlib.pyplot as plt
#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from .models import whatsapp, Film
from .forms import WhatsappForm, FilmForm
import os
import re
from django.db.models import Q
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
# dot='./media/'
dot = '/var/www/subdomain/whatsappdata/analysis/media/'
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
    df.to_csv(dot+'media/data.csv', index = False)
    return HttpResponse('hello world')


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
            
            #filename = "test1.txt"
            filename = dot + str(baseurls)

            # read file by lines
            #file_path = "whatsapp.txt"
            # f = open(filename, 'r')
            # f = open(filename, encoding="utf8")
            # data = f.readlines()
            # f.close()

            # # sanity stats
            # print('num lines: %s' %(len(data)))

            # # parse text and create list of lists structure
            # # remove first whatsapp info message
            # dataset = data[1:]
            # cleaned_data = []
            # for line in dataset:
            #     # grab the info and cut it out
            #     date = line.split(",")[0]
            #     line2 = line[len(date):]
            #     time = line2.split("-")[0][2:]
            #     line3 = line2[len(time):]
            #     name = line3.split(":")[0][4:]
            #     line4 = line3[len(name):]
            #     message = line4[6:-1] # strip newline charactor

            #     #print(date, time, name, message)
            #     cleaned_data.append([date, time, name, message])

            
            # # Create the DataFrame 
            # df = pd.DataFrame(cleaned_data, columns = ['Date', 'Time', 'Name', 'Message']) 
            # # print(df)
            # # check formatting 

            # if 0:
            #     print(df.head())
            #     print(df.tail())
            # print(df)
            # # Save it!
            # df.to_csv(dot+'media/data.csv', index=False)
            '''Convert WhatsApp chat log text file to a Pandas dataframe.'''

            # some regex to account for messages taking up multiple lines
            pat = re.compile(r'^(\d+\/\d+\/\d\d.*?)(?=^^\d+\/\d+\/\d\d\,\*?)', re.S | re.M)
            with open(filename, encoding = 'utf8') as raw:
                data = [m.group(1).strip().replace('\n', ' ') for m in pat.finditer(raw.read())]
            
            sender = []; message = []; datetime = []
            for row in data:

                # timestamp is before the first dash
                datetime.append(row.split(' - ')[0])

                # sender is between am/pm, dash and colon
                try:
                    s = re.search('M - (.*?):', row).group(1)
                    sender.append(s)
                except:
                    sender.append('')

                # message content is after the first colon
                try:
                    message.append(row.split(': ', 1)[1])
                except:
                    message.append('')

            df = pd.DataFrame(zip(datetime, sender, message), columns=['timestamp', 'sender', 'message'])
            df['timestamp'] = pd.to_datetime(df.timestamp, format='%m/%d/%y, %I:%M %p')

            # remove events not associated with a sender
            df = df[df.sender != ''].reset_index(drop=True)
            df.to_csv(dot+'media/data.csv', index=False)
            print('ok')

            # df = pd.read_csv(filename, header=0, encoding='utf8', on_bad_lines='skip')
            # df = pd.read_csv(filename, header=0, encoding='utf8', sep='-',)
            # df = pd.read_csv(filename, header=0, na_values=['NA'], delimiter='\t', encoding='utf8')
            # df = pd.read_csv(filename, header=None, names=['col1', 'col2', 'col3'], encoding='utf8')
            # # df = pd.read_csv(filename, header=None, delimiter='\t', encoding='utf8')
            # # df = pd.read_csv(filename, header=None, na_values=['NA'], encoding='utf8')
            #df.head()
            # df.to_csv(dot+'media/data.csv', index=False)
            with open(dot+'media/data.csv', 'r', encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Advance past the header
                for row in reader:
                    print(row)
                    # if len(row) == 1:
                    #     film, _ = Film.objects.get_or_create(title=row[0],)
                    #     film.save()
                    # elif len(row) == 2:
                    #     film, _ = Film.objects.get_or_create(title=row[0],
                    #     year=row[1],)
                    #     film.save()
                    # elif len(row) == 3:
                    #     film, _ = Film.objects.get_or_create(title=row[0],
                    #     year=row[1],
                    #     filmurl=row[2],)
                    #     film.save()
                    # elif len(row) == 4:
                        # print(row)
                        # print(len(row))

                        # genre, _ = Genre.objects.get_or_create(name=row[0])
                    print('passed')
                    # film, _ = Film.objects.get_or_create(title=row[0],
                    film, _ = Film.objects.get_or_create(title=row[0],                                   
                    year=row[1],
                    filmurl=row[2],)
                    # genre=row[3],)
                film.save()
                if os.path.exists(filename):
                    os.remove(filename)
                else:
                    print("That file does not exist!")
                return render(request, 'form_upload.html', {})
            #     for row in reader:
            #         print(row)

            # # genre, _ = Genre.objects.get_or_create(name=row[0])

            #         film, _ = Film.objects.get_or_create(title=row[0],
            #           year=row[1],
            #           filmurl = row[2],
            #           genre=row[3])
            #         # film, _ = Film.objects.get_or_create(title=row[3],
            #         #   year=row[4],
            #         #   filmurl = row[6],
            #         #   genre=row[2])
            #         film.save()
        #filedata = dot+'/media/data.csv'
        # dfjson = pd.read_csv(filedata , index_col=None, header=0,  encoding= 'unicode_escape')
        # #geeks = df.to_html()
        # json_records = dfjson.reset_index().to_json(orient ='records')
        # data = []
        # data = json.loads(json_records)
        return render(request, 'form_upload.html', {})
    else:
        form = WhatsappForm()
        documents = whatsapp.objects.all()
    return render(request, 'form_upload.html', {
        'form': form
    })
def indexhtml(request):
    filmes = Film.objects.all()
    return render(request, 'films.html', { 'filmes': filmes })

# def retrieve(request):
#     details=Film.objects.all().order_by('-id')
#     return render(request,'retrieve.html',{'details':details})

def edit(request,id):
    object=Film.objects.get(id=id)
    return render(request,'edit.html',{'object':object})

def update(request,id):
    object=Film.objects.get(id=id)
    form=FilmForm(request.POST,instance=object)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # object=Film.objects.all()
            return redirect('retrieve')
    return redirect('retrieve')

def delete(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Film, id = id)
 
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # home page
        # return HttpResponseRedirect("/")
        return redirect('retrieve')
 
    return render(request, "delete.html", context)

# def searchview(request):
#     if 'search' in request.GET:
#         search_term = request.GET['search']
#         search_result = whatsapp.objects.all().filter(chat__icontains=search_term)
#         return render(request, 'overview.html', {'articles' : articles, 'search_result': search_result })  
#     search_result = "Not Found"
#     articles = whatsapp.objects.all()
#     return render(request, 'overview.html', {'articles' : articles, 'search_result': search_result })    


#search box for django
def search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        # data = Film.objects.filter(filmurl__icontains=q)
        multiple_q = Q(Q(year__icontains=q) | Q(filmurl__icontains=q))
        details = Film.objects.filter(multiple_q)
        # object=Film.objects.get(id=id)
    else:
        details = Film.objects.all().order_by('-id')
    context = {
        'details': details
    }
    return render(request, 'search.html', context)

#check box delete
from django.views.generic import View
# from core import Film

class Product_view(View):
    
    def get(self, request):
        allproduct=Film.objects.all().order_by('-id')
        context={
            'details':allproduct
        }
        return render(request, "retrieve.html", context)
    def post(self, request, *args, **kwargs):
        if request.method=="POST":
            product_ids=request.POST.getlist('id[]')
            print(product_ids)
            for id in product_ids:
                # product = Film.object.get(pk=id)
                obj = get_object_or_404(Film, id = id)
                obj.delete()
            return redirect('retrieve')
