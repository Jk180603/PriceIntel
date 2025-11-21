import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="PriceIntel 3.0", layout="wide")
st.title("PriceIntel 3.0 – Ultimate E-Commerce Intelligence Board")
st.markdown("**iPhone 16 Pro 256GB • Live + Historical Analytics**")

BASE_PRICES = {"Amazon.de": 1299, "Zalando": 1249, "Otto.de": 1279, "MediaMarkt": 1239}

# Initialize persistent history
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Shop", "Price", "Time", "Date"])

placeholder = st.empty()

while True:
    # Generate realistic live prices
    current_prices = []
    for shop, base in BASE_PRICES.items():
        variation = random.randint(-40, 40)
        price = base + variation
        current_prices.append({
            "Shop": shop,
            "Price": price,
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Date": datetime.now().strftime("%Y-%m-%d")
        })
    
    df_now = pd.DataFrame(current_prices)
    
    # Append to history
    st.session_state.history = pd.concat([st.session_state.history, df_now], ignore_index=True)
    st.session_state.history = st.session_state.history.tail(200)  # Keep last 200 entries

    # === INTELLIGENCE CALCULATIONS ===
    current_best = df_now["Price"].min()
    current_avg = df_now["Price"].mean()
    historical_best = st.session_state.history["Price"].min()
    historical_worst = st.session_state.history["Price"].max()
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent_hist = st.session_state.history[st.session_state.history["Date"] >= seven_days_ago]
    week_low = recent_hist["Price"].min()
    week_high = recent_hist["Price"].max()

    # Add savings vs historical best
    df_now["Savings vs All-Time Best"] = (df_now["Price"] - historical_best).round(0).astype(int)
    df_now["Is Current Best"] = df_now["Price"] == current_best
    df_now["Is All-Time Best"] = df_now["Price"] == historical_best

    with placeholder.container():
        # TOP INTELLIGENCE BAR
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Best Price", f"€{int(current_best):,}", "Right now")
        c2.metric("All-Time Best Price", f"€{int(historical_best):,}", "Since launch")
        c3.metric("Current Average", f"€{int(current_avg):,}")
        c4.metric("7-Day Range", f"€{int(week_low):,} – €{int(week_high):,}")

        col1, col2 = st.columns([1.3, 1.7])

        with col1:
            st.subheader("Live Price Board")
            for _, row in df_now.sort_values("Price").iterrows():
                if row["Is All-Time Best"]:
                    st.markdown(f"**ALL-TIME BEST PRICE EVER**")
                if row["Is Current Best"]:
                    st.markdown(f"<h2 style='color:#00FF00'>→ {row['Shop']}</h2>", unsafe_allow_html=True)
                    st.write(f"**€{int(row['Price']):,}** ← **CURRENT BEST**")
                    st.success("CHEAPEST RIGHT NOW")
                else:
                    st.markdown(f"<h3 style='color:#FFFFFF'>→ {row['Shop']}</h3>", unsafe_allow_html=True)
                    st.write(f"**€{int(row['Price']):,}**")
                    st.warning(f"€{row['Savings vs All-Time Best']} more than all-time best")
                st.divider()

        with col2:
            st.subheader("Price History & Trend")
            chart_df = st.session_state.history.copy()
            chart_df["DateTime"] = pd.to_datetime(chart_df["Date"] + " " + chart_df["Time"])
            chart_df = chart_df.set_index("DateTime")
            st.line_chart(chart_df.pivot(columns="Shop", values="Price"), use_container_width=True)
            
            st.caption("Gold star = All-time best price ever recorded")

        st.success("PRICEINTEL 3.0 ACTIVE – Full Historical + Live Intelligence")
        st.caption("Built by Jay Khakhar • github.com/JK180603 • Ready for Audalaxy, Otto, Zalando")

    time.sleep(30)
