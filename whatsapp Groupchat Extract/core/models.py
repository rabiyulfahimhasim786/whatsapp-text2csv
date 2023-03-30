from django.db import models

class whatsapp(models.Model):
    chat = models.FileField(upload_to='media')

    def __str__(self):
        return self.chat

class Film(models.Model):
    title = models.TextField(blank=True)
    year = models.TextField(blank=True)
    filmurl = models.TextField(blank=True)
    # genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    genre = models.TextField(blank=True)
    
    def __str__(self):
        return self.title