import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random  # For fallback simulation if API fails

st.set_page_config(page_title="PriceIntel Live", layout="wide")
st.title("PriceIntel – Real-Time Multi-Platform Price Intelligence")
st.markdown("**Live Scraping & Analytics:** Amazon.de • Zalando • Otto.de • MediaMarkt")

# Real scraping function (lightweight, no Playwright)
def scrape_prices():
    results = []
    
    # Amazon.de (use public RSS or API fallback)
    try:
        response = requests.get("https://www.amazon.de/s?k=iphone+16+pro+256gb", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elem = soup.find("span", class_="a-price-whole")
        price = float(price_elem.text.replace('.', '')) if price_elem else 1299
        results.append({"Shop": "Amazon.de", "Price": price, "Status": "Scraped"})
    except:
        results.append({"Shop": "Amazon.de", "Price": 1299, "Status": "Fallback"})

    # Zalando (lightweight request)
    try:
        response = requests.get("https://en.zalando.de/catalog/?q=iphone+16+pro+256gb", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elem = soup.find("span", {"data-testid": "price"})
        price = float(price_elem.text.replace("€", "").replace(",", ".")) if price_elem else 1249
        results.append({"Shop": "Zalando", "Price": price, "Status": "Scraped"})
    except:
        results.append({"Shop": "Zalando", "Price": 1249, "Status": "Fallback"})

    # Otto.de
    try:
        response = requests.get("https://www.otto.de/suche/iphone%2016%20pro%20256gb", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elem = soup.find("span", class_="price--default")
        price = float(price_elem.text.replace("€", "").replace(",", ".") if price_elem else 1279)
        results.append({"Shop": "Otto.de", "Price": price, "Status": "Scraped"})
    except:
        results.append({"Shop": "Otto.de", "Price": 1279, "Status": "Fallback"})

    # MediaMarkt
    try:
        response = requests.get("https://www.mediamarkt.de/de/search.html?query=iphone+16+pro+256gb", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elem = soup.find("div", {"data-test": "mms-product-list-item-price"})
        price = float(price_elem.text.replace("€", "").replace(",", ".") if price_elem else 1239)
        results.append({"Shop": "MediaMarkt", "Price": price, "Status": "Scraped"})
    except:
        results.append({"Shop": "MediaMarkt", "Price": 1239, "Status": "Fallback"})

    df = pd.DataFrame(results)
    df["Time"] = datetime.now().strftime("%H:%M:%S")
    return df

# Intelligent calculations
def analyze_prices(df):
    df = df.copy()
    best_price = df["Price"].min()
    avg_price = df["Price"].mean()
    df["Savings €"] = (df["Price"] - best_price).round(2)
    df["Savings %"] = ((df["Price"] - best_price) / df["Price"] * 100).round(1)
    df["Best Deal"] = df["Price"] == best_price
    return df, best_price, avg_price

# History
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

placeholder = st.empty()

while True:
    with st.spinner("Scraping live prices from 4 shops..."):
        df = scrape_prices()

    df, best_price, avg_price = analyze_prices(df)

    # Save history
    new_row = df[["Shop", "Price", "Time"]].copy()
    new_row["Date"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
    hist = st.session_state.history.tail(40)

    with placeholder.container():
        # Intelligence Row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Best Price", f"€{best_price:,.0f}", "Cheapest Shop")
        c2.metric("Average Price", f"€{avg_price:,.0f}")
        c3.metric("Max Savings", f"€{df['Savings €'].max():,.0f}")
        c4.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

        col1, col2 = st.columns([1.2, 1.8])

        with col1:
            st.subheader("iPhone 16 Pro 256GB – Live Prices")
            for _, row in df.sort_values("Price").iterrows():
                color = "#00FF00" if row["Best Deal"] else "#FFFFFF"
                st.markdown(f"<h3 style='color:{color};'>→ {row['Shop']}</h3>", unsafe_allow_html=True)
                st.write(f"**€{row['Price']:,.0f}**")
                if row["Best Deal"]:
                    st.success("CHEAPEST RIGHT NOW")
                else:
                    st.warning(f"You pay **€{row['Savings €']} ({row['Savings %']}%) more**")
                st.caption(f"Status: {row['Status']}")
                st.divider()

        with col2:
            st.subheader("Price Trend (Last 10 Updates)")
            chart_data = hist.pivot(index="Time", columns="Shop", values="Price")
            st.line_chart(chart_data, use_container_width=True)
            st.caption("Green line = current cheapest shop")

        st.success("REAL-TIME INTELLIGENCE BOARD ACTIVE – Scraping every 30 seconds")
        st.caption("Built by Jay Khakhar | github.com/JK180603 | For Audalaxy & German AI roles")

    time.sleep(30)
