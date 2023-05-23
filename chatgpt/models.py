from django.db import models

# Create your models here.
# from django.db import models

class Chat(models.Model):
    input_text = models.TextField()
    output_text = models.TextField()


class Gpt(models.Model):
    input_query = models.TextField()
    output_query = models.TextField()