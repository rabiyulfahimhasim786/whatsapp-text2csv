from rest_framework import serializers
from .models import Chat, Gpt

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'input_text', 'output_text')


class GptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gpt
        fields = ('id', 'input_query', 'output_query')