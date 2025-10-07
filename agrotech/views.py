from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from datetime import datetime, date

from django.db.models import Count

from .models import Contact, ApmcRate, WeatherCity
from .forms import WeatherCityForm
from .weather import fetch_weather_for_city
from .plant_prediction import predict_disease
import joblib
import pandas as pd
import numpy as np
from django.shortcuts import render
from django import forms

# ----------------- Static Pages -----------------
def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def service(request):
    return render(request, "service.html")

def signin(request):
    return render(request, "signin.html")

def test(request):
    return render(request, "test.html")

def fertilizer(request):
    return render(request, "fertilizers.html")

def insurance(request):
    return render(request, "insurance.html")

def buy(request):
    return render(request, "buy.html")


# ----------------- Pune APMC History -----------------
def pune_apmc_history(request):
    dates = ApmcRate.objects.values("date").annotate(count=Count("id")).order_by("-date")
    selected_date = request.GET.get("date")

    rates = []
    if selected_date:
        rates = ApmcRate.objects.filter(date=selected_date).order_by("commodity")

    return render(request, "pune_apmc_history.html", {
        "dates": dates,
        "rates": rates,
        "selected_date": selected_date
    })


# ----------------- Pune APMC Scraper -----------------
def pune_apmc_scraper(request):
    url = "http://www.puneapmc.org/rates.aspx"
    base_url = "http://www.puneapmc.org/"
    message = ""

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        second_ul = soup.find_all('ul')[1]
        first_link = second_ul.find('a')['href']
        full_url = base_url + first_link

        response2 = requests.get(full_url)
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        tables = soup2.find_all('table')

        # ✅ Fix FutureWarning with StringIO
        dfs = [pd.read_html(StringIO(str(tbl)))[0] for tbl in tables]

        if dfs:
            final_df = pd.concat(dfs, ignore_index=True)
            final_df.columns = [str(c).lower().strip() for c in final_df.columns]

            today = date.today()

            for _, row in final_df.iterrows():
                try:
                    # ✅ Convert safely (no .strip() on int)
                    code = str(row.get('कोड नं.', '')).strip()
                    commodity = str(row.get('शेतिमाल', '')).strip()
                    unit = str(row.get('परिमाण', '')).strip()
                    arrival = str(row.get('आवक', 0)).strip()
                    min_price = str(row.get('किमान', '')).strip()
                    max_price = str(row.get('कमाल', '')).strip()

                    # Save into DB (update_or_create → keeps latest for same commodity+date)
                    ApmcRate.objects.update_or_create(
                        code=code,
                        commodity=commodity,
                        unit=unit,
                        arrival=arrival,
                        date=today,
                        defaults={
                            'min_price': min_price,
                            'max_price': max_price
                        }
                    )
                except Exception as e:
                    print("Row error:", e)

            message = "Data saved successfully!"
        else:
            message = "No data found."
    except Exception as e:
        message = f"Error: {e}"

    return render(request, "pune_apmc_scraper.html", {"message": message})


# ----------------- Pune APMC Table -----------------
def pune_apmc_table(request):
    url = "http://www.puneapmc.org/rates.aspx"
    base_url = "http://www.puneapmc.org/"

    table_html = "<p>Failed to load Pune APMC website</p>"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul_tags = soup.find_all('ul')
            if len(ul_tags) >= 2:
                second_ul = ul_tags[1]
                first_link = second_ul.find('a')
                if first_link and 'href' in first_link.attrs:
                    latest_link = first_link['href']
                    full_url = base_url + latest_link
                    response2 = requests.get(full_url)

                    if response2.status_code == 200:
                        soup2 = BeautifulSoup(response2.content, 'html.parser')
                        tables = soup2.find_all('table')

                        dfs = []
                        for tbl in tables:
                            df = pd.read_html(StringIO(str(tbl)))[0]
                            dfs.append(df)

                        if dfs:
                            final_df = pd.concat(dfs, ignore_index=True)
                            table_html = final_df.to_html(
                                classes="display",
                                index=False,
                                border=0
                            )
                        else:
                            table_html = "<p>No tables found</p>"
    except Exception as e:
        table_html = f"<p>Error: {str(e)}</p>"

    return render(request, "pune_apmc_table.html", {"table": table_html})


# ----------------- Weather Dashboard -----------------
TEMP_THRESHOLD = 35.0  # °C
WIND_THRESHOLD = 50.0  # km/h

def weather_dashboard(request):
    if request.method == "POST":
        form = WeatherCityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("weather_dashboard")
    else:
        form = WeatherCityForm()

    cities = WeatherCity.objects.all()
    alerts = []

    for city in cities:
        weather = fetch_weather_for_city(city.city)
        if weather:
            alert = None
            if weather["temperature"] > TEMP_THRESHOLD:
                alert = f"⚠️ Temperature alert for {city.city}: {weather['temperature']}°C"
            elif weather["windspeed"] > WIND_THRESHOLD:
                alert = f"⚠️ Wind speed alert for {city.city}: {weather['windspeed']} km/h"

            alerts.append({
                "id": city.id,  # <--- Make sure to include this
                "city": city.city,
                "weather": weather,
                "alert": alert
            })

    return render(request, "weather_dashboard.html", {
        "form": form,
        "alerts": alerts
    })


# ----------------- Contact Form -----------------
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, "contact.html")


# ----------------- Plant Disease Prediction -----------------
def predict_plant_disease(request):
    if request.method == "POST" and request.FILES.get("leaf_image"):
        image = request.FILES["leaf_image"]
        image_path = os.path.join(settings.MEDIA_ROOT, image.name)

        with open(image_path, "wb+") as f:
            for chunk in image.chunks():
                f.write(chunk)

        result = predict_disease(image_path)
        image_url = os.path.join(settings.MEDIA_URL, image.name)

        return render(request, "predict.html", {
            "uploaded": True,
            "image_url": image_url,
            "prediction": result
        })

    return render(request, "predict.html", {
        "uploaded": False,
        "image_url": None,
        "prediction": None
    })


# Load trained pipeline and label encoder once at startup
model_pipeline = joblib.load("fertilizer_xgb_pipeline.pkl")
le_target = joblib.load("le_target.pkl")

# Django Form
class FertilizerForm(forms.Form):
    crop = forms.CharField(label="Crop Name", max_length=100)
    season = forms.CharField(label="Season", max_length=100)
    soil_type = forms.CharField(label="Soil Type", max_length=100)
    ph = forms.FloatField(label="Soil pH")

# Soil pH advice
def soil_ph_advice(ph):
    if ph < 5.5:
        return "Soil is acidic → Add lime/dolomite to raise pH and improve nutrient availability."
    elif 5.5 <= ph <= 7.5:
        return "Soil pH is neutral → Good for most crops. No major amendment needed."
    else:
        return "Soil is alkaline → Add gypsum or organic matter to lower pH and improve structure."

# Prediction function
def predict_fertilizer(crop, season, soil_type, ph, top_n=3):
    crop = crop.strip().title()
    season = season.strip().title()
    soil_type = soil_type.strip().title()

    input_df = pd.DataFrame([[crop, season, soil_type, ph]],
                            columns=['Crop', 'Season', 'SoilType', 'pH'])

    # Predict probabilities
    probs = model_pipeline.predict_proba(input_df)[0]

    # Top N fertilizers
    top_indices = np.argsort(probs)[::-1][:top_n]
    top_fertilizers = [le_target.inverse_transform([i])[0] for i in top_indices]

    # Soil advice
    ph_message = soil_ph_advice(ph)
    fertilizers_formatted = "; ".join(top_fertilizers)

    return f"{ph_message}\nRecommended Fertilizers: {fertilizers_formatted}"

import requests
import json
from django.shortcuts import render
from .forms import FertilizerForm
from .soil_health import predict_fertilizer  # your trained ML function

# ====================
# OpenRouter / Gemini configuration
# ====================
OPENROUTER_API_KEY = "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"
GEMINI_MODEL = "google/gemini-2.5-pro"
GEMINI_URL = "https://openrouter.ai/api/v1/chat/completions"

def fertilizer_recommendation(request):
    result = None

    if request.method == "POST":
        form = FertilizerForm(request.POST)
        if form.is_valid():
            crop = form.cleaned_data['crop']
            season = form.cleaned_data['season']
            soil_type = form.cleaned_data['soil_type']
            ph = form.cleaned_data['ph']

            # -------------------
            # Step 1: ML model prediction
            # -------------------
            try:
                ml_result = predict_fertilizer(crop, season, soil_type, ph, top_n=3)
            except Exception as e:
                ml_result = f"❌ ML model could not generate recommendations: {str(e)}"

            # -------------------
            # Step 2: AI explanation using OpenRouter
            # -------------------
            prompt = f"""
            Suggest fertilizers for crop: {crop}, season: {season}, soil type: {soil_type}, pH: {ph}.
            The fertilizers recommended are: {ml_result}.
            Explain why these fertilizers are suitable. Keep it concise and actionable.
            """

            payload = {
                "model": GEMINI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an agriculture expert. Answer in plain text."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 1500
            }

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload), timeout=15)
                response.raise_for_status()
                data = response.json()

                # Proper handling of response
                if "choices" in data and len(data["choices"]) > 0:
                    ai_explanation = data["choices"][0]["message"]["content"]
                elif "error" in data:
                    ai_explanation = f"❌ AI explanation could not be generated: {data['error'].get('message', 'Unknown error')}"
                else:
                    ai_explanation = "❌ AI explanation could not be generated: Unexpected API response format."
            except Exception as e:
                ai_explanation = f"❌ AI explanation could not be generated: {str(e)}"

            result = {
                "recommendations": ml_result,
                "ai_explanation": ai_explanation
            }

    else:
        form = FertilizerForm()

    return render(request, "fertilizer_form.html", {"form": form, "result": result})



from django.shortcuts import redirect
from .models import WeatherCity  # Your city model

from django.shortcuts import redirect
from .models import WeatherCity

def remove_city(request, city_id):
    if request.method == "POST":
        try:
            city_obj = WeatherCity.objects.get(id=city_id)
            city_obj.delete()
        except WeatherCity.DoesNotExist:
            pass
    return redirect("weather_dashboard")
from django.shortcuts import render
from .forms import YieldPredictionForm
from .yield_predictor import predict_yield

def yield_prediction_view(request):
    result = None
    if request.method == "POST":
        form = YieldPredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = predict_yield(
                crop=data['crop'],
                season=data['season'],
                state=data['state'],
                area=data['area'],
                rainfall=data['rainfall'],
                fertilizer=data['fertilizer'],
                pesticide=data['pesticide']
            )
    else:
        form = YieldPredictionForm()
    return render(request, "yield_prediction.html", {"form": form, "result": result})
# views.py
from django.http import HttpResponse
from gtts import gTTS
import urllib.parse

def tts_audio(request):
    """
    Django view to generate audio from text using gTTS.
    Expects:
        ?text=Your+text+here&lang=mr
    Supports languages: en, hi, mr
    """
    text = request.GET.get('text', '')
    lang = request.GET.get('lang', 'en')  # default English

    if not text:
        return HttpResponse("No text provided", status=400)

    # Safety check for supported languages
    if lang not in ['en', 'hi', 'mr']:
        lang = 'en'

    try:
        tts = gTTS(text=text, lang=lang)
        response = HttpResponse(content_type="audio/mpeg")
        tts.write_to_fp(response)
        return response
    except Exception as e:
        return HttpResponse(f"Error generating audio: {e}", status=500)

