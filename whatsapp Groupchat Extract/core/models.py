from django.db import models

class whatsapp(models.Model):
    chat = models.FileField(upload_to='media')

    def __str__(self):
        return self.chat
