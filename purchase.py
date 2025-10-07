from flask import Flask, request, render_template, redirect
import pandas as pd
import os

app = Flask(__name__)

# File to store purchase details
DATA_FILE = "purchases.xlsx"

# Ensure the file exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Product", "Price", "Address", "Payment Method"])
    df.to_excel(DATA_FILE, index=False)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    if request.method == "POST":
        product = request.form["product"]
        price = request.form["price"]
        address = request.form["address"]
        payment_method = request.form["payment_method"]

        # Load existing data
        df = pd.read_excel(DATA_FILE)

        # Append new data
        new_data = pd.DataFrame([[product, price, address, payment_method]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)

        # Save to Excel
        df.to_excel(DATA_FILE, index=False)

        return redirect("/success")

    product = request.args.get("product")
    price = request.args.get("price")
    return render_template("purchase.html", product=product, price=price)

@app.route("/success")
def success():
    return "<h2>Purchase Successful! Your order has been placed.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
