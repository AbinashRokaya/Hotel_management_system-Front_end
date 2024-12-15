from django.db import models

# Create your models here.
from django.db import models

Rating =[
    (1,1),
    (2,2),
    (3,3),
    (4,4),
    (5,5)
]



# Create your models here.
class Hotel(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    rating = models.IntegerField(choices=Rating,default=None)
    contact = models.CharField(max_length=10)
    facilities = models.TextField()

    def __str__(self):
        return self.name