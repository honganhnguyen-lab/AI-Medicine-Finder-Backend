from django.db import models

# create class search by Text
# class SearchQuery(models.Model):
#     query = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

# create class upload Image
class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = 'api'

    def __str__(self):
        return f"Image {self.id} uploaded at {self.uploaded_at}"