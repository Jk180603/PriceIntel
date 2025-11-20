import streamlit as st
import pandas as pd
import random
from datetime import datetime
import time

st.set_page_config(page_title="PriceIntel Live", layout="wide")
st.title("PriceIntel – Real-Time E-Commerce Price Tracker")
st.caption("Amazon.de • Zalando • Otto.de • MediaMarkt – Live Demo")

# Simulate real scraped data (will be replaced by Playwright later)
def get_live_prices():
    base = {"Amazon.de": 1299, "Zalando": 1249, "Otto.de": 1279, "MediaMarkt": 1239}
    data = []
    for shop, price in base.items():
        current_price = price + random.randint(-30, 30)
        data.append({
            "Shop": shop,
            "Price (€)": current_price,
            "Time": datetime.now().strftime("%H:%M:%S")
        })
    df = pd.DataFrame(data)
    df["Savings"] = df["Price (€)"].max() - df["Price (€)"]
    df["Best Deal"] = df["Savings"] == df["Savings"].max()
    return df

# History in session state
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

placeholder = st.empty()

while True:
    df = get_live_prices()

    # Save to history
    new = df[["Shop", "Price (€)", "Time"]].copy()
    new["Date"] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.history = pd.concat([st.session_state.history, new.rename(columns={"Price (€)": "Price"})], ignore_index=True)
    hist = st.session_state.history.tail(40)

    with placeholder.container():
        c1, c2 = st.columns([1, 2])

        with c1:
            st.subheader("iPhone 16 Pro 256GB – Live Prices")
            for _, r in df.iterrows():
                color = "#00FF00" if r["Best Deal"] else "#FFFFFF"
                st.markdown(f"<h2 style='color:{color};'>→ {r['Shop']}</h2>", unsafe_allow_html=True)
                st.metric("Price", f"€{r['Price (€)']:,}", f"Save €{int(r['Savings'])}" if r['Savings']>0 else None)
                st.caption(f"Updated {r['Time']}")
                st.divider()

        with c2:
            st.subheader("Price Trend (Last Updates)")
            chart_data = hist.copy()
            chart_data["DateTime"] = chart_data["Date"] + " " + chart_data["Time"]
            st.line_chart(chart_data.pivot(index="DateTime", columns="Shop", values="Price"), use_container_width=True)

        st.success("LIVE TRACKING ACTIVE – Updates every 30 seconds")
        st.caption("Built by Jay Khakhar • github.com/JK180603")

    time.sleep(30)
