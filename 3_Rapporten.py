import streamlit as st
from database import init_db, get_restaurant
from translations import t

st.set_page_config(page_title="Rapporten", page_icon="📊", layout="wide")
init_db()

if "lang" not in st.session_state:
    st.session_state.lang = "nl"
if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None

lang = st.session_state.lang

st.title(t("reports", lang))

if not st.session_state.restaurant_id:
    st.warning(t("select_restaurant", lang))
    st.stop()

restaurant = get_restaurant(st.session_state.restaurant_id)
st.success(f"{t('selected_restaurant', lang)}: {restaurant[1]}")
st.info(t("coming_later", lang))
