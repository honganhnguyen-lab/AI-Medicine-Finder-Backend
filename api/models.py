from django.db import models

# create class search by Text
class SearchQuery(models.Model):
    query = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
