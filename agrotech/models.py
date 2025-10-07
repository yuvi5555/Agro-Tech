from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return self.name
class ApmcRate(models.Model):
    code = models.CharField(max_length=20, blank=True, null=True)
    commodity = models.CharField(max_length=100)
    unit = models.CharField(max_length=50, blank=True, null=True)
    arrival = models.FloatField(blank=True, null=True)
    min_price = models.CharField(max_length=50, blank=True, null=True)
    max_price = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.commodity} ({self.date})"
class APMCRecord(models.Model):
    code = models.CharField(max_length=20)
    commodity = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    arrival = models.FloatField()
    min_price = models.CharField(max_length=50)
    max_price = models.CharField(max_length=50)
    date = models.DateField()

    def __str__(self):
        return f"{self.code} - {self.commodity} ({self.date})"
class WeatherCity(models.Model):
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.city