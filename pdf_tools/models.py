from django.db import models

class UploadedPdf(models.Model):
    file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.file.name
