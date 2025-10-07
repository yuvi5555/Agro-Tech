from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    apmc = request.form['apmc']
    date = request.form['date']

    # Map APMC to district/market values
    district_market_map = {
        "pune": ("Pune", "Pune Market"),
        "sambhajinagar": ("Aurangabad", "Sambhajinagar Market"),
        "nashik": ("Nashik", "Nashik Market"),
        "ahilyanagar": ("Indore", "Ahilyanagar Market"),
        "mumbai": ("Mumbai", "Mumbai Market")
    }

    district, market = district_market_map.get(apmc, (None, None))
    if not district or not market:
        return "Invalid APMC selection", 400

    # Scrape the data from Napanta
    url = "https://www.napanta.com/market-price/"
    payload = {"district": district, "market": market, "date": date}

    response = requests.post(url, data=payload)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the commodity data
    data = []
    rows = soup.select("table tbody tr")
    for row in rows:
        columns = row.find_all("td")
        if columns:
            data.append({
                "commodity": columns[0].text.strip(),
                "variety": columns[1].text.strip(),
                "max_price": columns[2].text.strip(),
                "min_price": columns[3].text.strip(),
                "avg_price": columns[4].text.strip(),
            })

    return render_template('display.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)






