
import streamlit as st
import pandas as pd
from datetime import date

from database import (
    init_db, get_restaurants, get_restaurant, add_restaurant,
    update_restaurant, delete_restaurant, add_crew, update_crew,
    get_crew, delete_crew, calculate_age
)
from translations import t

st.set_page_config(page_title="RestoCheck", page_icon="✅", layout="wide")
init_db()

if "lang" not in st.session_state:
    st.session_state.lang = "nl"
if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "dashboard"

st.markdown("""
<style>
.card {
    background: #ffffff;
    border: 1px solid #eeeeee;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    min-height: 145px;
    margin-bottom: 10px;
}
.card-icon {font-size: 2.8rem; line-height: 1; margin-bottom: 12px;}
.card-title {font-size: 1.25rem; font-weight: 800; margin-bottom: 6px;}
.card-text {color: #666; font-size: 0.98rem;}
.selected-resto {
    background: linear-gradient(90deg, #ffbc0d 0%, #fff2bd 100%);
    border: 2px solid #ffbc0d;
    border-radius: 20px;
    padding: 18px 22px;
    font-weight: 900;
    margin-bottom: 20px;
    color: #222;
    font-size: 1.15rem;
}
.employee-card {
    border: 1px solid #eee;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 12px;
    background: #fff;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
}
</style>
""", unsafe_allow_html=True)

def status_label(status, lang):
    labels = {
        "student": f"🎓 {t('student', lang)}",
        "vast": f"💼 {t('fixed', lang)}",
        "flexi": f"⚡ {t('flexi', lang)}",
        "interim": f"🧾 {t('interim', lang)}",
    }
    return labels.get(status, status)

def show_card(icon, title, text):
    st.markdown(f"""
    <div class="card">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div class="card-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)

def nav_card(icon, title, text, target, key):
    show_card(icon, title, text)
    if st.button(f"{icon} Open {title}", key=key, use_container_width=True):
        st.session_state.active_tab = target
        st.rerun()

def selected_restaurant_banner(lang):
    if st.session_state.restaurant_id:
        resto = get_restaurant(st.session_state.restaurant_id)
        if resto:
            status = "🟢 Actief" if resto[3] else "🔴 Inactief"
            st.markdown(
                f"<div class='selected-resto'>🏢 {t('current_restaurant', lang)}: {resto[1]} &nbsp;&nbsp; {status}</div>",
                unsafe_allow_html=True
            )
            return resto
    st.warning(f"⚠️ {t('no_selected_restaurant', lang)}")
    return None

lang_labels = {"nl": "Nederlands", "fr": "Français", "en": "English"}

with st.sidebar:
    st.session_state.lang = st.selectbox(
        "🌍 Taal / Langue / Language",
        options=list(lang_labels.keys()),
        format_func=lambda x: lang_labels[x],
        index=list(lang_labels.keys()).index(st.session_state.lang),
    )
    st.divider()

    nav_options = {
        "dashboard": f"🏠 {t('dashboard', st.session_state.lang)}",
        "restaurants": f"🏢 {t('restaurants', st.session_state.lang)}",
        "crew": f"👥 {t('crew', st.session_state.lang)}",
        "roster": f"📅 {t('roster_check', st.session_state.lang)}",
        "reports": f"📊 {t('reports', st.session_state.lang)}",
    }

    chosen_label = st.radio(
        "Menu",
        list(nav_options.values()),
        index=list(nav_options.keys()).index(st.session_state.active_tab),
    )
    st.session_state.active_tab = list(nav_options.keys())[list(nav_options.values()).index(chosen_label)]

    st.divider()
    st.caption("✅ RestoCheck")
    if st.session_state.restaurant_id:
        resto = get_restaurant(st.session_state.restaurant_id)
        if resto:
            st.success(f"🏢 {resto[1]}")

lang = st.session_state.lang
restaurants = get_restaurants()

st.title(f"✅ {t('app_title', lang)}")
st.caption(t("subtitle", lang))

if st.session_state.active_tab != "dashboard":
    selected_restaurant_banner(lang)

if st.session_state.active_tab == "dashboard":
    if st.session_state.restaurant_id:
        selected_restaurant_banner(lang)

    st.subheader(f"🏢 {t('select_restaurant', lang)}")
    if not restaurants:
        st.info(t("no_restaurant", lang))
    else:
        options = {f"{name} {'✅' if active else '⛔'}": rid for rid, name, address, active in restaurants}
        selected_label = st.selectbox(t("select_restaurant", lang), list(options.keys()))
        if st.button(f"🚀 {t('open_restaurant', lang)}", type="primary", use_container_width=True):
            st.session_state.restaurant_id = options[selected_label]
            st.success(f"✅ {t('selected_restaurant', lang)}: {selected_label}")
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        nav_card("🏢✏️", t("restaurants", lang), t("restaurant_help", lang), "restaurants", "nav_restaurants")
    with c2:
        nav_card("👥➕", t("crew", lang), t("crew_help", lang), "crew", "nav_crew")
    c3, c4 = st.columns(2)
    with c3:
        nav_card("📅🔍", t("roster_check", lang), t("check_help", lang), "roster", "nav_roster")
    with c4:
        nav_card("📊📄", t("reports", lang), t("report_help", lang), "reports", "nav_reports")

elif st.session_state.active_tab == "restaurants":
    st.header(f"🏢 {t('restaurants', lang)}")
    add_tab, edit_tab, delete_tab = st.tabs([
        f"🏢➕ {t('add_restaurant', lang)}",
        f"🏢✏️ {t('edit_restaurant', lang)}",
        f"🏢🗑️ {t('delete_restaurant', lang)}",
    ])

    with add_tab:
        show_card("🏢➕", t("add_restaurant", lang), t("restaurant_help", lang))
        with st.form("add_restaurant_form"):
            name = st.text_input(f"🏢 {t('restaurant_name', lang)}")
            address = st.text_input(f"📍 {t('address', lang)}")
            active = st.checkbox(f"🟢 {t('active', lang)}", value=True)
            if st.form_submit_button(f"💾 {t('save', lang)}"):
                if name.strip():
                    try:
                        add_restaurant(name, address, active)
                        st.success(f"✅ {t('saved', lang)}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error(t("restaurant_name", lang))

    with edit_tab:
        show_card("🏢✏️", t("edit_restaurant", lang), t("restaurant_help", lang))
        restaurants = get_restaurants()
        if restaurants:
            edit_map = {name: rid for rid, name, address, active in restaurants}
            edit_name = st.selectbox(f"🏢 {t('select_restaurant', lang)}", list(edit_map.keys()), key="edit_restaurant_select")
            selected = get_restaurant(edit_map[edit_name])
            with st.form("edit_restaurant_form"):
                new_name = st.text_input(f"🏢 {t('restaurant_name', lang)}", value=selected[1])
                new_address = st.text_input(f"📍 {t('address', lang)}", value=selected[2] or "")
                new_active = st.checkbox(f"🟢 {t('active', lang)}", value=bool(selected[3]))
                if st.form_submit_button(f"💾 {t('save', lang)}"):
                    update_restaurant(selected[0], new_name, new_address, new_active)
                    st.success(f"✅ {t('saved', lang)}")
                    st.rerun()
        else:
            st.info(t("no_restaurant", lang))

    with delete_tab:
        show_card("🏢🗑️", t("delete_restaurant", lang), t("restaurant_help", lang))
        restaurants = get_restaurants()
        if restaurants:
            delete_map = {name: rid for rid, name, address, active in restaurants}
            delete_name = st.selectbox(f"🏢 {t('select_restaurant', lang)}", list(delete_map.keys()), key="delete_restaurant_select")
            confirm = st.checkbox(f"⚠️ {t('confirm_delete', lang)}")
            if st.button(f"🗑️ {t('delete', lang)}", disabled=not confirm, use_container_width=True):
                delete_restaurant(delete_map[delete_name])
                if st.session_state.restaurant_id == delete_map[delete_name]:
                    st.session_state.restaurant_id = None
                st.success(f"✅ {t('deleted', lang)}")
                st.rerun()
        else:
            st.info(t("no_restaurant", lang))

elif st.session_state.active_tab == "crew":
    st.header(f"👥 {t('crew', lang)}")
    resto = get_restaurant(st.session_state.restaurant_id) if st.session_state.restaurant_id else None

    if not resto:
        st.warning(f"⚠️ {t('no_selected_restaurant', lang)}")
    else:
        add_crew_tab, overview_tab, edit_tab = st.tabs([
            f"👤➕ {t('new_employee', lang)}",
            f"📋 {t('crew_list', lang)}",
            f"👤✏️ {t('edit', lang)}",
        ])

        status_options = {"student": t("student", lang), "vast": t("fixed", lang), "flexi": t("flexi", lang), "interim": t("interim", lang)}

        with add_crew_tab:
            show_card("👤➕", t("add_crew", lang), t("crew_help", lang))
            with st.form("add_crew_form"):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input(f"👤 {t('first_name', lang)}")
                    last_name = st.text_input(f"👤 {t('last_name', lang)}")
                    birthdate = st.date_input(f"🎂 {t('birthdate', lang)}", value=date(2000, 1, 1), min_value=date(1940, 1, 1), max_value=date.today())
                    age = calculate_age(birthdate.isoformat())
                    st.info(f"🎂 {t('age_today', lang)}: **{age}** | 👶 {t('is_minor', lang)}: **{t('yes', lang) if age < 18 else t('no', lang)}**")
                with col2:
                    status_label_value = st.radio(f"🏷️ {t('status', lang)}", list(status_options.values()), horizontal=True)
                    status = [k for k, v in status_options.items() if v == status_label_value][0]
                    contract_hours = None
                    if status == "vast":
                        st.warning(f"⏰ {t('contract_info', lang)}")
                        contract_hours = st.number_input(f"⏰ {t('contract_hours', lang)}", min_value=1.0, max_value=60.0, step=0.5, value=38.0)
                    function = st.text_input(f"🧩 {t('function', lang)}")
                    department = st.text_input(f"🍟 {t('department', lang)}")
                    active = st.checkbox(f"🟢 {t('active', lang)}", value=True)
                    notes = st.text_area(f"📝 {t('notes', lang)}")
                if st.form_submit_button(f"💾 {t('save', lang)}", type="primary", use_container_width=True):
                    if not first_name.strip() or not last_name.strip():
                        st.error(f"{t('first_name', lang)} / {t('last_name', lang)}")
                    elif status == "vast" and not contract_hours:
                        st.error(t("contract_required", lang))
                    else:
                        add_crew(st.session_state.restaurant_id, first_name, last_name, birthdate.isoformat(), status, contract_hours, function, department, notes, active)
                        st.success(f"✅ {t('employee_saved', lang)}: {first_name} {last_name}")
                        st.balloons()

        with overview_tab:
            rows = get_crew(st.session_state.restaurant_id)
            if not rows:
                st.info(t("employees", lang))
            else:
                for row in rows:
                    crew_id, first_name, last_name, birthdate, status, contract_hours, function, department, notes, active = row
                    age = calculate_age(birthdate)
                    st.markdown(f"""
                    <div class="employee-card">
                        <div style="font-size:1.25rem;font-weight:800;">👤 {first_name} {last_name}</div>
                        <div>🎂 {age} jaar | 👶 {t('is_minor', lang)}: {t('yes', lang) if age < 18 else t('no', lang)}</div>
                        <div>🏷️ {status_label(status, lang)}</div>
                        <div>⏰ {t('contract_hours', lang)}: {contract_hours if contract_hours else '-'}</div>
                        <div>🧩 {t('function', lang)}: {function if function else '-'}</div>
                        <div>🍟 {t('department', lang)}: {department if department else '-'}</div>
                        <div>{'🟢' if active else '🔴'} {t('active', lang) if active else t('inactive', lang)}</div>
                        <div>📝 {notes if notes else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        if st.button(f"👤✏️ {t('edit', lang)}", key=f"edit_go_{crew_id}", use_container_width=True):
                            st.session_state["edit_crew_id"] = crew_id
                            st.info("Ga naar tab 👤✏️ Bewerken om dit profiel aan te passen.")
                    with c2:
                        if st.button(f"🗑️ {t('delete_profile', lang)}", key=f"quick_delete_{crew_id}", use_container_width=True):
                            delete_crew(crew_id)
                            st.success(f"✅ {t('employee_deleted', lang)}: {first_name} {last_name}")
                            st.rerun()

        with edit_tab:
            rows = get_crew(st.session_state.restaurant_id)
            if not rows:
                st.info(t("employees", lang))
            else:
                default_index = 0
                if "edit_crew_id" in st.session_state:
                    for i, r in enumerate(rows):
                        if r[0] == st.session_state["edit_crew_id"]:
                            default_index = i
                            break

                crew_map = {f"{r[2]} {r[1]}": r for r in rows}
                names = list(crew_map.keys())
                selected_name = st.selectbox("👤 Kies crewlid", names, index=default_index)
                selected = crew_map[selected_name]
                crew_id, first_name, last_name, birthdate, status, contract_hours, function, department, notes, active = selected

                with st.form("edit_crew_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_first_name = st.text_input(f"👤 {t('first_name', lang)}", value=first_name)
                        new_last_name = st.text_input(f"👤 {t('last_name', lang)}", value=last_name)
                        new_birthdate = st.date_input(f"🎂 {t('birthdate', lang)}", value=date.fromisoformat(birthdate), min_value=date(1940, 1, 1), max_value=date.today())
                    with col2:
                        label_values = list(status_options.values())
                        current_label = status_options.get(status, t("student", lang))
                        new_status_label = st.radio(f"🏷️ {t('status', lang)}", label_values, index=label_values.index(current_label), horizontal=True)
                        new_status = [k for k, v in status_options.items() if v == new_status_label][0]
                        new_contract_hours = None
                        if new_status == "vast":
                            st.warning(f"⏰ {t('contract_info', lang)}")
                            new_contract_hours = st.number_input(f"⏰ {t('contract_hours', lang)}", min_value=1.0, max_value=60.0, step=0.5, value=float(contract_hours or 38.0))
                        new_function = st.text_input(f"🧩 {t('function', lang)}", value=function or "")
                        new_department = st.text_input(f"🍟 {t('department', lang)}", value=department or "")
                        new_active = st.checkbox(f"🟢 {t('active', lang)}", value=bool(active))
                        new_notes = st.text_area(f"📝 {t('notes', lang)}", value=notes or "")

                    if st.form_submit_button(f"💾 {t('save', lang)}", use_container_width=True):
                        update_crew(crew_id, new_first_name, new_last_name, new_birthdate.isoformat(), new_status, new_contract_hours, new_function, new_department, new_notes, new_active)
                        st.success(f"✅ {t('employee_saved', lang)}: {new_first_name} {new_last_name}")
                        st.rerun()

elif st.session_state.active_tab == "roster":
    st.header(f"📅🔍 {t('roster_check', lang)}")
    resto = get_restaurant(st.session_state.restaurant_id) if st.session_state.restaurant_id else None
    if not resto:
        st.warning(f"⚠️ {t('no_selected_restaurant', lang)}")
    else:
        c1, c2 = st.columns(2)
        with c1:
            show_card("📥", "Rooster importeren", "Upload hier straks het roosterbestand.")
        with c2:
            show_card("🔍", "Controle uitvoeren", "Hier koppelen we de bestaande wettelijke controlelogica.")
        uploaded_file = st.file_uploader("📥 Upload roosterbestand", type=["xlsx", "xls", "csv"])
        if uploaded_file:
            st.success("✅ Bestand opgeladen.")
            try:
                if uploaded_file.name.lower().endswith(".csv"):
                    preview = pd.read_csv(uploaded_file)
                else:
                    preview = pd.read_excel(uploaded_file)
                st.subheader("👀 Voorbeeld van import")
                st.dataframe(preview.head(20), use_container_width=True)
            except Exception as e:
                st.error(f"Kon bestand nog niet lezen: {e}")

elif st.session_state.active_tab == "reports":
    st.header(f"📊 {t('reports', lang)}")
    resto = get_restaurant(st.session_state.restaurant_id) if st.session_state.restaurant_id else None
    if not resto:
        st.warning(f"⚠️ {t('no_selected_restaurant', lang)}")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            show_card("⚠️", "Overtredingen", "Overzicht van wettelijke fouten.")
        with c2:
            show_card("👶", "Minderjarigen", "Controle volgens leeftijd.")
        with c3:
            show_card("⏰", "Contracturen", "Controle voor vaste medewerkers.")
        st.info(t("coming_later", lang))
