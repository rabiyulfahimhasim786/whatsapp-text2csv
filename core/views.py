from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
import regex
import pandas as pd
import numpy as np
import emoji
import csv
import unicodedata

import json
from collections import Counter
from django.shortcuts import get_object_or_404
import matplotlib.pyplot as plt
#from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from .models import whatsapp, Film
from .forms import WhatsappForm, FilmForm, LocationChoiceField, LabelChoiceField, DateChoiceField
from rest_framework.response import Response
from django.contrib import messages
import os
import re
from django.db.models import Q
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
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
# dot = '/var/www/subdomain/whatsappdata/analysis/media/'
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
            
            # Read the existing CSV file
            # dft = pd.read_csv(dot+'media/data.csv')

            # # Split date and time components
            # dft['date'] = dft['timestamp'].str.split(' ').str[0]
            # dft['time'] = dft['timestamp'].str.split(' ').str[1]

            # # Remove the timestamp column
            # dft.drop('timestamp', axis=1, inplace=True)

            # # Reorder the columns
            # cols = ['date', 'time'] + [col for col in dft.columns if col not in ['date', 'time']]
            # dft = dft[cols]

            # # Save the modified DataFrame back to the CSV file
            # dft.to_csv(dot+'media/datas.csv', index=False)

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
                    # film, _ = Film.objects.get_or_create(title=row[0],                                   
                    # year=row[1],
                    # filmurl=row[2],)
                    # # genre=row[3],)
                    # if row[2] == '<Media omitted>':
                    #     print(row[2])
                    #     continue
                    # elif row[2] == 'Waiting for this message':
                    #     print(row[2])
                    #     continue
                    # else:
                    #     film, _ = Film.objects.get_or_create(title=row[0],                                   
                    #     year=row[1],
                    #     filmurl=row[2],)
                    #     # genre=row[3],)
                    # film.save()
                    datetime_str = row[0]  # Assuming the datetime is in the first column

                    # Extract the time component
                    datee_str = datetime_str.split()[0]
                    time_str = datetime_str.split()[1]
                    # print(time_str)
                    if row[2] == '<Media omitted>' or row[2] == 'Waiting for this message':
                        # print(row[2])
                        continue
                    else:
                        film, created = Film.objects.get_or_create(
                            date=datee_str,
                            # title=row[0],
                            title=time_str,
                            year=row[1],
                            filmurl=row[2],
                            # genre=row[3],
                        )
                        if created:
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

   
    return render(request,'edit.html',{'object':object,}) #'sources': sources})
from django.http import HttpResponseRedirect

def update(request,id):
    my_model = get_object_or_404(Film, id=id)
    if request.method == 'POST':
        form = FilmForm(request.POST, instance=my_model)
        if form.is_valid():
            form.save()
            if 'save_home' in request.POST:
                return redirect('home')
            elif 'save_next' in request.POST:
                try:
                    next_model = Film.objects.filter(id__gt=id).filter(dropdownlist='New').order_by('id')[0]
                    return redirect('edit', id=next_model.id)
                except IndexError:
                    return render(request, 'navigation.html')
            elif 'save_continue' in request.POST:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif 'delete_d' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(id)
                # for id in delete_idd:
                    # product = Film.object.get(pk=id)
                    # obj = get_object_or_404(Film, id = id)
                    # obj.delete()
                # id = request.POST.get('idd')
                # id = id
                # obj = get_object_or_404(Film, id=id)
                # obj.delete()
                try:

                    next_model = Film.objects.filter(id__gt=id).filter(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                    obj = get_object_or_404(Film, id=id)
                    id=next_model.id
                    
                    # obj = get_object_or_404(Film, id=id)
                    obj.delete()
                    return redirect('edit', id)
                except IndexError:
                    return render(request, 'navigation.html')
            elif 'delete_dynamic' in request.POST:
                # try:

                #     next_model = Film.objects.filter(id__gt=id).filter(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                #     obj = get_object_or_404(Film, id=id)
                    
                #     context ={}
 
                #     # fetch the object related to passed id
                #     obj = get_object_or_404(Film, id = id)
                
                #     id=next_model.id
                #     if request.method =="POST":
                #         # delete object
                #         obj.delete()
                #         print('deleteworking')
                #         return redirect('edit', id)
                    
                #     # obj = get_object_or_404(Film, id=id)
                #     # obj.delete()
                #     return redirect('edit', id)
                # except IndexError:
                #     return render(request, 'navigation.html')
                try:
                    next_model = Film.objects.filter(id__gt=id).filter(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                    obj = get_object_or_404(Film, id=id)
                    id = next_model.id
                    obj.delete()
                    return redirect('edit', id)
                except IndexError:
                    obj = get_object_or_404(Film, id=id)
                    obj.delete()
                    return render(request, 'navigation.html')
    else:
        form = FilmForm(instance=my_model)
    
    # my_model = Film.objects.get(id=id)
    # if request.method == 'POST':
    #     form = FilmForm(request.POST, instance=my_model)
    #     if form.is_valid():
    #         form.save()
    #         if 'save_home' in request.POST:
    #             return redirect('home')
    #         elif 'save_next' in request.POST:
    #             try:
    #                 next_model = Film.objects.filter(id__gt=id).order_by('id')[0]
    #                 return redirect('edit',id=next_model.id)
    #             except Film.DoesNotExist:
    #                 pass
    # else:
    #     form = FilmForm(instance=my_model)

    # object=Film.objects.get(id=id)
    # print(object)
    # form=FilmForm(request.POST,instance=object)
    # if request.method == 'POST':
    #     if form.is_valid():
    #         form.save()
    #         # object=Film.objects.all()
    #         return redirect('home')

            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return redirect(request.META['HTTP_REFERER'])
    # return redirect('retrieve')
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect(request.META['HTTP_REFERER'])

def leadedit(request,id):
    object=Film.objects.get(id=id)

   
    return render(request,'leadsedit.html',{'object':object,})

# def leadupdate(request,id):
#     my_model = get_object_or_404(Film, id=id)
#     if request.method == 'POST':
#         form = FilmForm(request.POST, instance=my_model)
#         if form.is_valid():
#             form.save()
#             # delete_idd=request.POST.get('id')
#             if 'save_home' in request.POST:
#                 return redirect('leads')
#             elif 'save_next' in request.POST:
#                 try:
#                     next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').order_by('id')[0]
#                     return redirect('leadedit', id=next_model.id)
#                 except IndexError:
#                     return render(request, 'navigation.html')
#             elif 'save_continue' in request.POST:
#                 return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#             elif 'save_convert' in request.POST:
#                 status = Film.objects.get(id=id)
#                 print(status)
#                 status.checkstatus^= 1
#                 status.save()
#                 try:
#                     next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
#                     return redirect('leadedit', id=next_model.id)
#                 except IndexError:
#                     return render(request, 'navigation.html')
                
#             elif 'delete_d' in request.POST:
#                 # snippet_ids=request.POST.getlist('ids[]')
#                 print(id)
#                 try:

#                     next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
#                     obj = get_object_or_404(Film, id=id)
#                     id=next_model.id
                    
#                     # obj = get_object_or_404(Film, id=id)
#                     obj.delete()
#                     return redirect('leadedit', id)
#                 except IndexError:
#                     return render(request, 'navigation.html')
#             elif 'delete_dynamic' in request.POST:
        
#                 try:
#                     next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
#                     obj = get_object_or_404(Film, id=id)
#                     id = next_model.id
#                     obj.delete()
#                     return redirect('leadedit', id)
#                 except IndexError:
#                     obj = get_object_or_404(Film, id=id)
#                     obj.delete()
#                     return render(request, 'navigation.html')
               
#     else:
#         form = FilmForm(instance=my_model)
#     return redirect(request.META['HTTP_REFERER'])

def delete(request, id):

    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Film, id = id)
 
 
    if request.method =="POST":
        # delete object
        obj.delete()
     
        return redirect('home')
 
    return render(request, "delete.html", context)

import requests

def leadupdate(request,id):
    my_model = get_object_or_404(Film, id=id)
    if request.method == 'POST':
        form = FilmForm(request.POST, instance=my_model)
        if form.is_valid():
            form.save()
            # delete_idd=request.POST.get('id')
            if 'save_home' in request.POST:
                return redirect('leads')
            elif 'save_next' in request.POST:
                try:
                    next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').order_by('id')[0]
                    return redirect('leadedit', id=next_model.id)
                except IndexError:
                    return render(request, 'navigation.html')
            elif 'save_continue' in request.POST:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif 'save_convert' in request.POST:
                status = Film.objects.get(id=id)
                print(status)
                status.checkstatus^= 1
                status.save()
                try:
                    next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                    return redirect('leadedit', id=next_model.id)
                except IndexError:
                    return render(request, 'navigation.html')
            elif 'delete_d' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(id)
                try:
                    next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                    obj = get_object_or_404(Film, id=id)
                    id=next_model.id
                    # obj = get_object_or_404(Film, id=id)
                    obj.delete()
                    return redirect('leadedit', id)
                except IndexError:
                    return render(request, 'navigation.html')
            elif 'delete_dynamic' in request.POST:
                try:
                    next_model = Film.objects.filter(id__gt=id).exclude(dropdownlist='New').filter(checkstatus=1).order_by('id')[0]
                    obj = get_object_or_404(Film, id=id)
                    id = next_model.id
                    obj.delete()
                    return redirect('leadedit', id)
                except IndexError:
                    obj = get_object_or_404(Film, id=id)
                    obj.delete()
                    return render(request, 'navigation.html')
            elif 'chiliadstaffingapi' in request.POST:
                # Call first A
                id = my_model.id
                if id==id:
                    year = my_model.year
                    filmurl = my_model.filmurl
                    # replacements = [('%', ''), ('&', 'and'), ('∷', '')]

                    # for char, replacement in replacements:
                    #     if char in filmurl:
                    #         filmurl = filmurl.replace(char, replacement)

                    # print(filmurl)
                    # originaldata = re.sub(r'\W+', '', filmurl)
                    # print(originaldata)
                    unwanted = "[%]"
                    originaldata = re.sub(unwanted, '', filmurl)
                    
                    title = my_model.title
                    url = f"https://chiliadstaffing.com/dynamic/chiliadstaffingapi.php?action=lead&phone={year}&message={originaldata}&date={title}"
                    # api_params = {
                    #     'action': 'lead',
                    #     'phone': my_model.year,
                    #     'message': my_model.filmurl,
                    #     'date': my_model.title,
                    # }
                    # response = requests.get(api_url, params=api_params)
                    response = requests.get(url)
                    print(response.text)  # Print the response from the API
                    status = Film.objects.get(id=id)
                    print(status)
                    status.checkstatus^= 1
                    status.save()
                    # return redirect('leads')
                    return redirect('search')
                return redirect('leadedit', id)
                    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
            elif 'careerdesssapi' in request.POST:
                # Call second API
                # try:
                #     api_url = 'https://career.desss.com/dynamic/careerdesssapi.php'
                #     api_params = {
                #         'action': 'lead',
                #         'phone': my_model.year,
                #         'message': my_model.filmurl,
                #         'date': my_model.title,
                #     }
                #     response = requests.get(api_url, params=api_params)
                #     print(response.text)  # Print the response from the API
                #     return redirect('leads')
                # except:
                #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                id = my_model.id
                if id==id:
                    year = my_model.year
                    filmurl = my_model.filmurl
                    # replacements = [('%', ''), ('&', 'and')]

                    # for char, replacement in replacements:
                    #     if char in filmurl:
                    #         originaldata = filmurl.replace(char, replacement)

                    # print(originaldata)
                    unwanted = "[%]"
                    originaldata = re.sub(unwanted, '', filmurl)
                    
                    title = my_model.title
                    url = f"https://career.desss.com/dynamic/careerdesssapi.php?action=lead&phone={year}&message={originaldata}&date={title}"
                    # api_params = {
                    #     'action': 'lead',
                    #     'phone': my_model.year,
                    #     'message': my_model.filmurl,
                    #     'date': my_model.title,
                    # }
                    # response = requests.get(api_url, params=api_params)
                    response = requests.get(url)
                    print(response.text)  # Print the response from the API
                    # return render(request, 'confirmation.html')
                    status = Film.objects.get(id=id)
                    print(status)
                    status.checkstatus^= 1
                    status.save()
                    # return redirect('leads')
                    return redirect('search')
                return redirect('leadedit', id)
    else:
        form = FilmForm(instance=my_model)
    return redirect(request.META['HTTP_REFERER'])

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
    location_list = LocationChoiceField()
    label_list = LabelChoiceField()
    if 'q' in request.GET:
        q = request.GET['q']
        # data = Film.objects.filter(filmurl__icontains=q)
        multiple_q = Q(Q(year__icontains=q) | Q(filmurl__icontains=q))
        details = Film.objects.filter(multiple_q).filter(Q(checkstatus=0))
        # object=Film.objects.get(id=id)
    elif request.GET.get('locations'):
        selected_location = request.GET.get('locations')
        details = Film.objects.filter(checkstatus=selected_location)
    elif request.GET.get('label'):
        labels = request.GET.get('label')
        details = Film.objects.filter(dropdownlist=labels)
    else:
        details = Film.objects.all().order_by('-id')
    context = {
        'details': details,
        'location_list': location_list,
        'label_list': label_list
    }
    return render(request, 'search.html', context)

#check box delete
from django.views.generic import View
# from core import Film

class Product_view(View):
    
    # def get(self, request):
    #     # allproduct=Film.objects.all().order_by('-id')
    #     allproduct=Film.objects.all().order_by('-id')
    #     context={
    #         'details':allproduct
    #     }
    #     # queryset = Film.objects.filter(checkstatus__in=str(0))
    #     # print(queryset)
    #     return render(request, "retrieve.html", context)
    def get(self,  request):
        # location_list = LocationChoiceField()
        label_list = LabelChoiceField()
        # datesdatalist = DateChoiceField()


        if 'q' in request.GET:
            q = request.GET['q']
            # data = Film.objects.filter(filmurl__icontains=q)
            multiple_q = Q(Q(year__icontains=q) | Q(filmurl__icontains=q))
            details = Film.objects.filter(multiple_q).filter(Q(dropdownlist='New'))
            # object=Film.objects.get(id=id)
        elif request.GET.get('locations'):
            selected_location = request.GET.get('locations')
            details = Film.objects.filter(checkstatus=selected_location)
        elif request.GET.get('label'):
            labels = request.GET.get('label')
            details = Film.objects.filter(dropdownlist=labels)#.filter(dropdownlist='New')
        elif request.GET.get('datesdata'):
            selected_datedata = request.GET.get('datesdata')
            details = Film.objects.filter(dropdownlist='New',title=selected_datedata)
        else:
            # details = Film.objects.all().order_by('-id')
            # details = Film.objects.filter(dropdownlist='New').order_by('-id')
            details = Film.objects.filter(dropdownlist='New').order_by('id')
        context = {
            'details': details,
            # 'location_list': location_list,
            'label_list': label_list,
            # 'datesdatalist': datesdatalist,
           
        }
        return render(request, 'retrieve.html', context)

    def post(self, request, *args, **kwargs):
        # if request.method=="POST":
        #     product_ids=request.POST.getlist('id[]')
        #     # if product_ids == product_ids:
        #     product_ids=request.POST.getlist('id[]')
        #     print(product_ids)
        #     for id in product_ids:
        #         # product = Film.object.get(pk=id)
        #         obj = get_object_or_404(Film, id = id)
        #         obj.delete()
        #     return redirect('retrieve')
         if request.method=="POST":
            product_ids=request.POST.getlist('id[]')
            # if product_ids == product_ids:
            snippet_ids=request.POST.getlist('ids[]')
            delete_idd=request.POST.get('id')
            print(product_ids)
            print(snippet_ids)
            if 'id[]' in request.POST:
                print(product_ids)
                for id in product_ids:
                    # product = Film.object.get(pk=id)
                    obj = get_object_or_404(Film, id = id)
                    obj.delete()
                return redirect('home')
            elif 'ids[]' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(snippet_ids)
                for id in snippet_ids:
                    # product = Film.object.get(pk=id)
                    # obj = get_object_or_404(Film, id = id)
                    # obj.delete()
                    print(id)
                    status = Film.objects.get(id=id)
                    print(status)
                    status.checkstatus^= 1
                    status.save()
                return redirect('home')
            elif 'id' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(delete_idd)
                # for id in delete_idd:
                    # product = Film.object.get(pk=id)
                    # obj = get_object_or_404(Film, id = id)
                    # obj.delete()
                # id = request.POST.get('idd')
                id = delete_idd
                obj = get_object_or_404(Film, id=id)
                obj.delete()
                
                return redirect('home')
            else:
                return redirect('home')

                

class Leads_view(View):
    
    # def get(self, request):
    #     # allproduct=Film.objects.all().order_by('-id')
    #     allproduct=Film.objects.all().order_by('-id')
    #     context={
    #         'details':allproduct
    #     }
    #     # queryset = Film.objects.filter(checkstatus__in=str(0))
    #     # print(queryset)
    #     return render(request, "retrieve.html", context)
    def get(self,  request):
        # location_list = LocationChoiceField()
        label_list = LabelChoiceField()

        if 'q' in request.GET:
            q = request.GET['q']
            # data = Film.objects.filter(filmurl__icontains=q)
            multiple_q = Q(Q(year__icontains=q) | Q(filmurl__icontains=q))
            details = Film.objects.filter(multiple_q).filter(~Q(dropdownlist='New'))
            # object=Film.objects.get(id=id)
        elif request.GET.get('locations'):
            selected_location = request.GET.get('locations')
            details = Film.objects.filter(checkstatus=selected_location)
        elif request.GET.get('label'):
            labels = request.GET.get('label')
            details = Film.objects.filter(dropdownlist=labels)
        else:
            # details = Film.objects.all().order_by('-id')
            # details = Film.objects.exclude(dropdownlist='New').order_by('-id')
            details = Film.objects.exclude(dropdownlist='New').order_by('id')
        context = {
            'details': details,
            # 'location_list': location_list,
            'label_list': label_list
        }
        return render(request, 'leadtype.html', context)

    def post(self, request, *args, **kwargs):
        # if request.method=="POST":
        #     product_ids=request.POST.getlist('id[]')
        #     # if product_ids == product_ids:
        #     product_ids=request.POST.getlist('id[]')
        #     print(product_ids)
        #     for id in product_ids:
        #         # product = Film.object.get(pk=id)
        #         obj = get_object_or_404(Film, id = id)
        #         obj.delete()
        #     return redirect('retrieve')
         if request.method=="POST":
            product_ids=request.POST.getlist('id[]')
            # if product_ids == product_ids:
            snippet_ids=request.POST.getlist('ids[]')
            delete_idd=request.POST.get('id')
            print(product_ids)
            print(snippet_ids)
            if 'id[]' in request.POST:
                print(product_ids)
                for id in product_ids:
                    # product = Film.object.get(pk=id)
                    obj = get_object_or_404(Film, id = id)
                    obj.delete()
                return redirect('home')
            elif 'ids[]' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(snippet_ids)
                for id in snippet_ids:
                    # product = Film.object.get(pk=id)
                    # obj = get_object_or_404(Film, id = id)
                    # obj.delete()
                    print(id)
                    status = Film.objects.get(id=id)
                    print(status)
                    status.checkstatus^= 1
                    status.save()
                return redirect('leads')
            elif 'id' in request.POST:
                # snippet_ids=request.POST.getlist('ids[]')
                print(delete_idd)
                # for id in delete_idd:
                    # product = Film.object.get(pk=id)
                    # obj = get_object_or_404(Film, id = id)
                    # obj.delete()
                # id = request.POST.get('idd')
                id = delete_idd
                obj = get_object_or_404(Film, id=id)
                obj.delete()
                
                return redirect('leads')
            else:
                return redirect('leads')

                



        # else:
        #     print('working snippet')
        #     snippet_ids=request.POST.getlist('ids[]')
        #     print(snippet_ids)
        #     for id in snippet_ids:
        #         # product = Film.object.get(pk=id)
        #         # obj = get_object_or_404(Film, id = id)
        #         # obj.delete()
        #          print(id)
        #          status = Film.objects.get(id=id)
        #          print(status)
        #          status.checkstatus^= 1
        #          status.save()
        #     return redirect('retrieve')


    # def posting(self, request, *args, **kwargs):
    #     if request.method=="POST":
    #         snippet_ids=request.POST.getlist('ids[]')
    #         print(snippet_ids)
    #         for id in snippet_ids:
    #             # product = Film.object.get(pk=id)
    #             # obj = get_object_or_404(Film, id = id)
    #             # obj.delete()
    #              print(id)
    #              status = Film.objects.get(id=id)
    #              print(status)
    #              status.checkstatus^= 1
    #              status.save()
    #         return redirect(request.META['HTTP_REFERER'])
    


def status(request,id):
    # status = Film.objects.get(id=pk)
    # w = Film.objects.get(id=request.POST['id'])
    # w.is_working = request.POST['checkstatus'] == '1'
    # w.save()
    status = Film.objects.get(id=id)
    print(status)
    status.checkstatus^= 1
    status.save()
    return redirect(request.META['HTTP_REFERER'])
    

from core.serializers import SnippetSerializer
class SnippetList(ListCreateAPIView):
    serializer_class = SnippetSerializer

    # def get_queryset(self):
    #     # Get URL parameter as a string, if exists 
    #     ids = self.request.query_params.get('ids', None)
    #     print(ids)
    #     # Get snippets for ids if they exist
    #     if ids is not None:
    #         # try:
    #         # Convert parameter string to list of integers
    #         ids = [ int(x) for x in ids.split(',') ]
    #         # Get objects for all parameter ids 
    #         # queryset = Film.objects.filter(pk__in=ids)
    #         for id in ids:
    #             status = Film.objects.get(id=id)
    #             print(status)
    #             # queryset = get_object_or_404(Film, pk__in=str(id))
    #             if int(status.checkstatus) == 1:
    #                     status.checkstatus^= 1
    #                     print(status.checkstatus)
    #                     status.save()
    #             # queryset = get_object_or_404(Film, pk__in= str(id))
    #         queryset = Film.objects.filter(pk__in=ids)
    #         # queryset = Film.objects.filter(checkstatus__in=str(0))
    #         return queryset
    #         # except:
    #         #     return Response({"status": "Notfound"})
    #     else:
    #         # Else no parameters, return all objects
    #         queryset = Film.objects.all()
    #         return queryset
    #         # return queryset
    #         # queryset = Film.objects.filter(checkstatus__in=str(1))

        # return queryset

    # def get_list_filter(self):
    #     queryset = Film.objects.all()
    #     # queryset = Film.objects.filter(checkstatus__in=str(1))
    #     print(queryset)
    #     return queryset


    
    def get_queryset(self):
        try:
            # Get URL parameter as a string, if exists 
            ids = self.request.query_params.get('ids', None)
            # print(ids)
            # Get snippets for ids if they exist
            if ids is not None:
                # Convert parameter string to list of integers
                ids = [ int(x) for x in ids.split(',') ]
                # Get objects for all parameter ids 
                # queryset = Film.objects.filter(pk__in=ids)
                for id in ids:
                    status = Film.objects.get(id=id)
                    print(status)
                    if int(status.checkstatus) == 1:
                            status.checkstatus^= 1
                            print(status.checkstatus)
                            status.save()
                    # queryset = get_object_or_404(Film, pk__in= str(id))
                queryset = Film.objects.filter(pk__in=ids)
                # queryset = Film.objects.filter(checkstatus__in=str(0))
                return queryset
            else:
                # Else no parameters, return all objects
                queryset = Film.objects.all()
                # queryset = Film.objects.filter(checkstatus__in=str(1))
                return queryset
        except:
            # return None
            return Response({
                "details": None
            }),



# def locations(request):


#     location_list = LocationChoiceField()

#     if request.GET.get('locations'):
#         selected_location = request.GET.get('locations')
#         details = Film.objects.filter(checkstatus=selected_location)
#     elif 'q' in request.GET:
#         q = request.GET['q']
#         # data = Film.objects.filter(filmurl__icontains=q)
#         multiple_q = Q(Q(year__icontains=q) | Q(filmurl__icontains=q))
#         details = Film.objects.filter(multiple_q)
#         # object=Film.objects.get(id=id)
#     # else:
#     #     details = Film.objects.all().order_by('-id')
#     else:
#         details = Film.objects.all().order_by('-id')


#     context = {
#         'query_results': details,
#         'location_list': location_list,

#     }
#     return render(request,'locations.html', context)


# date filterations

def event_filter(request):
    form = EventFilterForm(request.GET or None)
    events = []

    if form.is_valid():
        events = form.filter_events()

    context = {
        'form': form,
        'events': events
    }
    return render(request, 'event_filter.html', context)