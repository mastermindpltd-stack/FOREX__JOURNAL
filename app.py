import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

from auth import get_authenticator
from database import create_table, get_connection

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Clean Trading Journal", layout="wide")

# -------------------------------------------------
# UPLOAD FOLDER
# -------------------------------------------------
UPLOAD_DIR = "uploads/screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------------------------
# CLEAN DARK UI (ANDROID FRIENDLY)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
}

.stApp {
  background:#0e1117;
  color:#e6edf3;
}

/* Cards */
.card {
  background:#161b22;
  border-radius:16px;
  padding:16px;
  box-shadow:0 8px 24px rgba(0,0,0,.35);
}
.card-title {
  color:#9da7b1;
  font-size:13px;
}
.card-value {
  color:#58a6ff;
  font-size:26px;
  font-weight:700;
}

/* Buttons */
.stButton>button {
  border-radius:12px;
  background:#58a6ff;
  color:#0e1117;
  font-weight:600;
}
.stButton>button:hover {
  background:#79c0ff;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
  background:#0e1117;
  color:#e6edf3;
  border-radius:12px;
}

/* Tables */
[data-testid="stDataFrame"] {
  background:#0e1117;
  border-radius:16px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOGIN
# -------------------------------------------------
authenticator = get_authenticator()
name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("Wrong username or password")
    st.stop()

if auth_status is None:
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"Welcome {name}")

# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------
page = st.sidebar.radio("Menu", ["Dashboard", "Add Trade", "Trades"])

# -------------------------------------------------
# DATABASE INIT
# -------------------------------------------------
create_table()

# -------------------------------------------------
# LOAD USER TRADES
# -------------------------------------------------
conn = get_connection()
df = pd.read_sql(
    "SELECT * FROM trades WHERE username = ? ORDER BY created_at",
    conn,
    params=(username,)
)
conn.close()

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
if page == "Dashboard":
    st.header("📊 Dashboard")

    if df.empty:
        st.info("No trades yet")
        st.stop()

    # Calculations
    df["PnL"] = df.apply(
        lambda r:
        (r["takeprofit"] - r["entry"]) * r["lot"]
        if r["direction"] == "Buy"
        else (r["entry"] - r["takeprofit"]) * r["lot"],
        axis=1
    )

    df["Equity"] = df["PnL"].cumsum()

    def card(title, value):
        st.markdown(f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div class="card-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: card("Trades", len(df))
    with c2: card("Win Rate", f"{round((df['PnL']>0).mean()*100,2)}%")
    with c3: card("Net PnL", round(df["PnL"].sum(),2))

    fig = px.line(df, y="Equity")
    fig.update_traces(line=dict(width=3, color="#58a6ff"))
    fig.update_layout(
        height=360,
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="#e6edf3",
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(gridcolor="#21262d")
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# ADD TRADE
# -------------------------------------------------
elif page == "Add Trade":
    st.header("➕ Add Trade")

    with st.form("trade_form"):
        pair = st.text_input("Pair (example: EURUSD)")
        direction = st.radio("Direction", ["Buy", "Sell"], horizontal=True)
        entry = st.number_input("Entry", format="%.5f")
        stoploss = st.number_input("Stoploss", format="%.5f")
        takeprofit = st.number_input("Takeprofit", format="%.5f")
        lot = st.number_input("Lot Size", min_value=0.01, step=0.01)
        submit = st.form_submit_button("Save Trade")

    if submit:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO trades
            (username, pair, direction, entry, stoploss, takeprofit, lot)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (username, pair, direction, entry, stoploss, takeprofit, lot)
        )
        conn.commit()
        conn.close()

        st.success("Trade added successfully")
        st.rerun()

# -------------------------------------------------
# TRADES + SCREENSHOT + NOTES
# -------------------------------------------------
elif page == "Trades":
    st.header("📒 Trades")

    if df.empty:
        st.info("No trades yet")
        st.stop()

    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📸 Screenshot & Notes")

    trade_id = st.selectbox("Select Trade ID", df["id"].tolist())
    uploaded_img = st.file_uploader(
        "Upload TradingView Screenshot",
        type=["png", "jpg", "jpeg"]
    )
    notes = st.text_area("Notes (why I entered, mistakes, emotions)")

    if st.button("Save Screenshot"):
        if uploaded_img is None:
            st.error("Please upload an image")
        else:
            filename = f"{username}_{trade_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            filepath = os.path.join(UPLOAD_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(uploaded_img.getbuffer())

            conn = get_connection()
            conn.execute(
                "UPDATE trades SET screenshot = ?, notes = ? WHERE id = ?",
                (filepath, notes, trade_id)
            )
            conn.commit()
            conn.close()

            st.success("Screenshot saved")
            st.rerun()

    review = df[df["id"] == trade_id].iloc[0]

    if review["screenshot"]:
        st.image(review["screenshot"], use_column_width=True)

    if review["notes"]:
        st.info(review["notes"])
