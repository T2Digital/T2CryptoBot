
import streamlit as st
import requests

API_BASE_URL = "https://t2cryptobot.onrender.com"

st.set_page_config(page_title="T2CryptoBot Pro 🐳", layout="wide")
st.title("📊 T2CryptoBot Pro 🐳")

if "token" not in st.session_state:
    st.subheader("🔐 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        try:
            r = requests.post(f"{API_BASE_URL}/login", data={"username": username, "password": password})
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                st.success("✅ تم تسجيل الدخول")
            else:
                st.error("❌ فشل تسجيل الدخول")
        except requests.exceptions.RequestException:
            st.error("🚫 تعذر الاتصال بالخادم.")
    st.stop()

with st.sidebar:
    st.header("⚙️ إعدادات التحليل")
    symbol = st.selectbox("زوج التداول", ["BTC/USDT", "ETH/USDT"])
    timeframe = st.selectbox("الإطار الزمني", ["5m", "15m", "1h", "4h"])
    risk_reward = st.slider("نسبة المخاطرة", 1.0, 5.0, 3.0)
    st.markdown("---")
    st.subheader("💎 اشتراكك")
    try:
        r = requests.get(f"{API_BASE_URL}/subscription", params={"token": st.session_state.token})
        if r.status_code == 200:
            sub = r.json()
            st.markdown(f"**الباقة:** {sub['plan']}")
            st.markdown(f"**صالح حتى:** {sub['expires']}")
        else:
            st.warning("تعذر جلب الاشتراك.")
    except requests.exceptions.RequestException:
        st.warning("⚠️ لا يمكن الوصول إلى الاشتراك الآن.")

if st.button("🔍 تحليل وإشارة"):
    with st.spinner("جاري التحليل..."):
        try:
            r = requests.post(
                f"{API_BASE_URL}/generate-signal",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                json={"symbol": symbol, "timeframe": timeframe, "risk_reward": risk_reward}
            )
            if r.status_code == 200:
                res = r.json()
                st.success(f"✅ الإشارة: {res['signal']}\nالسعر: {res['price']}\nوقف الخسارة: {res['stop_loss']}\nأخذ الربح: {res['take_profit']}")
            else:
                st.error("❌ فشل التحليل أو انتهاء الجلسة.")
        except requests.exceptions.RequestException:
            st.error("🚫 تعذر الاتصال بالسيرفر.")
