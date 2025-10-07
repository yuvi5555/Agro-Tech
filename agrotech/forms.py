from django import forms
from .models import WeatherCity

class WeatherCityForm(forms.ModelForm):
    class Meta:
        model = WeatherCity
        fields = ['city']  # Only city name
from django import forms

CROP_CHOICES = [
    ("Arecanut", "Arecanut"), ("Arhar/Tur", "Arhar/Tur"), ("Castor seed", "Castor seed"),
    ("Coconut", "Coconut"), ("Cotton(lint)", "Cotton(lint)"), ("Rice", "Rice"),
    ("Wheat", "Wheat"), ("Maize", "Maize")
]

SEASON_CHOICES = [("Kharif", "Kharif"), ("Rabi", "Rabi"), ("Whole Year", "Whole Year")]
STATE_CHOICES = [("Assam", "Assam"), ("Punjab", "Punjab"), ("Tamil Nadu", "Tamil Nadu"), ("Maharashtra", "Maharashtra")]

class YieldPredictionForm(forms.Form):
    crop = forms.ChoiceField(choices=CROP_CHOICES)
    season = forms.ChoiceField(choices=SEASON_CHOICES)
    state = forms.ChoiceField(choices=STATE_CHOICES)
    area = forms.FloatField()
    rainfall = forms.FloatField()
    fertilizer = forms.FloatField()
    pesticide = forms.FloatField()
class FertilizerForm(forms.Form):
    crop = forms.CharField(max_length=100)
    season = forms.CharField(max_length=50)
    soil_type = forms.CharField(max_length=50)
    ph = forms.FloatField()