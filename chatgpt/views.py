from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Hello World')

from django.shortcuts import render,redirect

from django.http import HttpResponse
import json
from django.http import HttpResponse, JsonResponse

from rest_framework.response import Response
from .serializers import ChatSerializer, GptSerializer

from .models import Chat, Gpt

from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import serializers
import openai

# Create your views here.
def chatgptindex(request):
    return HttpResponse("Hello, world !")
projectapi_key = "your-api-key"


class ChatView(ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def post(self, request):
        input_text = request.data.get('input_text')
        if not input_text:
            input_text = request.query_params.get('input_text')
        openai.api_key = projectapi_key
        output_text = openai.Completion.create(
            engine="text-davinci-003",
            prompt=input_text,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        ).choices[0].text
        # Split the output text based on a specific delimiter (e.g. newline character)
        # output_array = output_text.split('\n')
        # datalist = list(filter(lambda x: len(x) > 0, output_array))
        response = json.loads(output_text)
        print(response)        
        details = ['H1', 'H2', 'MetaTitle', 'Content', 'MetaKeywords', 'MetaMisc']

        output_dict = {}

        for detail in details:
            if int(len(response)) == 6:
                output_dict = response
            elif detail in response:
                output_dict[detail] = response[detail]
            else:
                output_dict[detail] = ""

        # print(output_dict)
        #dumping output into json format for double quotations
        output_text = json.dumps(output_dict)

        print(output_text)
        #saving into database
        chat = Chat.objects.create(input_text=input_text, output_text=output_text)
        #chat = Chat.objects.create(input_text=input_text, output_text=output_dict)
        serializer = ChatSerializer(chat)
        return Response(serializer.data)



class ChatUpdateDeleteApiView(RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]


class GptView(ListCreateAPIView):
    queryset = Gpt.objects.all()
    serializer_class = GptSerializer

    def post(self, request):
        input_query = request.data.get('input_query')
        if not input_query:
            input_query = request.query_params.get('input_query')
        openai.api_key = projectapi_key
        output_query = openai.Completion.create(
            engine="text-davinci-003",
            prompt=input_query,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        ).choices[0].text
        # Split the output text based on a specific delimiter (e.g. newline character)
        # output_array = output_text.split('\n')
        # datalist = list(filter(lambda x: len(x) > 0, output_array))
        # response = json.loads(output_text)
        # print(output_query)        
        # details = ['H1', 'H2', 'MetaTitle', 'Content', 'MetaKeywords', 'MetaMisc']

        # output_dict = {}

        # for detail in details:
        #     if int(len(response)) == 6:
        #         output_dict = response
        #     elif detail in response:
        #         output_dict[detail] = response[detail]
        #     else:
        #         output_dict[detail] = ""

        # print(output_dict)
        chat = Gpt.objects.create(input_query=input_query, output_query=output_query)
        serializer = GptSerializer(chat)
        return Response(serializer.data)


class GptUpdateDeleteApiView(RetrieveUpdateDestroyAPIView):
    queryset = Gpt.objects.all()
    serializer_class = GptSerializer
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]