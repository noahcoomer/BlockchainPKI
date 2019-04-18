from django.db import models

# Create your models here.
class Block(models.Model):
    header = models.CharField(max_length=25)
    hashValue = models.CharField(max_length=25)

    def __str__(self):
        return self.header
    class Meta:
        verbose_name_plural = 'blocks'
