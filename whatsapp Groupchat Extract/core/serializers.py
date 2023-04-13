from rest_framework import routers, serializers, viewsets

from . models import whatsapp,Film
class SnippetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = "__all__"