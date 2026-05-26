
import streamlit as st
from datetime import date

from database import (
    init_db, get_restaurants, get_restaurant, add_restaurant,
    update_restaurant, delete_restaurant, add_crew, get_crew,
    delete_crew, calculate_age
)
from translations import t

st.set_page_config(page_title="RestoCheck", page_icon="✅", layout="wide")
init_db()

if "lang" not in st.session_state:
    st.session_state.lang = "nl"
if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None

st.markdown("""
<style>
.card {
    background: #ffffff;
    border: 1px solid #eeeeee;
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    min-height: 145px;
    margin-bottom: 18px;
}
.card-icon {font-size: 2.8rem; line-height: 1; margin-bottom: 12px;}
.card-title {font-size: 1.25rem; font-weight: 800; margin-bottom: 6px;}
.card-text {color: #666; font-size: 0.98rem;}
.selected-resto {
    background: #fff7df;
    border: 1px solid #ffbc0d;
    border-radius: 18px;
    padding: 16px 20px;
    font-weight: 700;
    margin-bottom: 20px;
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
    st.markdown(
        f"""
        <div class="card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def selected_restaurant_banner(lang):
    if st.session_state.restaurant_id:
        resto = get_restaurant(st.session_state.restaurant_id)
        if resto:
            st.markdown(
                f"<div class='selected-resto'>🏢 {t('current_restaurant', lang)}: {resto[1]}</div>",
                unsafe_allow_html=True,
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
    st.caption("✅ RestoCheck")
    if st.session_state.restaurant_id:
        resto = get_restaurant(st.session_state.restaurant_id)
        if resto:
            st.success(f"🏢 {resto[1]}")

lang = st.session_state.lang
restaurants = get_restaurants()

st.title(f"✅ {t('app_title', lang)}")
st.caption(t("subtitle", lang))

tab_dashboard, tab_restaurants, tab_crew, tab_roster, tab_reports = st.tabs([
    f"🏠 {t('dashboard', lang)}",
    f"🏢 {t('restaurants', lang)}",
    f"👥 {t('crew', lang)}",
    f"📅 {t('roster_check', lang)}",
    f"📊 {t('reports', lang)}",
])

with tab_dashboard:
    if st.session_state.restaurant_id:
        selected_restaurant_banner(lang)

    st.subheader(f"🏢 {t('select_restaurant', lang)}")

    if not restaurants:
        st.info(t("no_restaurant", lang))
    else:
        options = {f"{name} {'✅' if active else '⛔'}": rid for rid, name, address, active in restaurants}
        selected_label = st.selectbox(t("select_restaurant", lang), list(options.keys()))
        if st.button(f"🚀 {t('open_restaurant', lang)}", type="primary"):
            st.session_state.restaurant_id = options[selected_label]
            st.success(f"{t('selected_restaurant', lang)}: {selected_label}")
            st.rerun()

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        show_card("🏢✏️", t("restaurants", lang), t("restaurant_help", lang))
    with c2:
        show_card("👥➕", t("crew", lang), t("crew_help", lang))
    c3, c4 = st.columns(2)
    with c3:
        show_card("📅🔍", t("roster_check", lang), t("check_help", lang))
    with c4:
        show_card("📊📄", t("reports", lang), t("report_help", lang))

with tab_restaurants:
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
            submitted = st.form_submit_button(f"💾 {t('save', lang)}")
            if submitted:
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
                submitted = st.form_submit_button(f"💾 {t('save', lang)}")
                if submitted:
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
            if st.button(f"🗑️ {t('delete', lang)}", disabled=not confirm):
                delete_restaurant(delete_map[delete_name])
                if st.session_state.restaurant_id == delete_map[delete_name]:
                    st.session_state.restaurant_id = None
                st.success(f"✅ {t('deleted', lang)}")
                st.rerun()
        else:
            st.info(t("no_restaurant", lang))

with tab_crew:
    st.header(f"👥 {t('crew', lang)}")
    resto = selected_restaurant_banner(lang)

    if resto:
        add_crew_tab, overview_tab = st.tabs([
            f"👤➕ {t('new_employee', lang)}",
            f"📋 {t('crew_list', lang)}",
        ])

        status_options = {
            "student": t("student", lang),
            "vast": t("fixed", lang),
            "flexi": t("flexi", lang),
            "interim": t("interim", lang),
        }

        with add_crew_tab:
            show_card("👤➕", t("add_crew", lang), t("crew_help", lang))

            with st.form("add_crew_form"):
                col1, col2 = st.columns(2)

                with col1:
                    first_name = st.text_input(f"👤 {t('first_name', lang)}")
                    last_name = st.text_input(f"👤 {t('last_name', lang)}")
                    birthdate = st.date_input(
                        f"🎂 {t('birthdate', lang)}",
                        value=date(2000, 1, 1),
                        min_value=date(1940, 1, 1),
                        max_value=date.today(),
                    )
                    age = calculate_age(birthdate.isoformat())
                    st.info(
                        f"🎂 {t('age_today', lang)}: **{age}** | "
                        f"👶 {t('is_minor', lang)}: **{t('yes', lang) if age < 18 else t('no', lang)}**"
                    )

                with col2:
                    status_label_value = st.selectbox(f"🏷️ {t('status', lang)}", list(status_options.values()))
                    status = [k for k, v in status_options.items() if v == status_label_value][0]

                    contract_hours = None
                    if status == "vast":
                        contract_hours = st.number_input(
                            f"⏰ {t('contract_hours', lang)}",
                            min_value=1.0,
                            max_value=60.0,
                            step=0.5,
                            value=38.0,
                        )

                    function = st.text_input(f"🧩 {t('function', lang)}")
                    department = st.text_input(f"🍟 {t('department', lang)}")
                    active = st.checkbox(f"🟢 {t('active', lang)}", value=True)
                    notes = st.text_area(f"📝 {t('notes', lang)}")

                submitted = st.form_submit_button(f"💾 {t('save', lang)}", type="primary")
                if submitted:
                    if not first_name.strip() or not last_name.strip():
                        st.error(f"{t('first_name', lang)} / {t('last_name', lang)}")
                    elif status == "vast" and not contract_hours:
                        st.error(t("contract_required", lang))
                    else:
                        add_crew(
                            restaurant_id=st.session_state.restaurant_id,
                            first_name=first_name,
                            last_name=last_name,
                            birthdate=birthdate.isoformat(),
                            status=status,
                            contract_hours=contract_hours,
                            function=function,
                            department=department,
                            notes=notes,
                            active=active,
                        )
                        st.success(f"✅ {t('employee_saved', lang)}")
                        st.rerun()

        with overview_tab:
            rows = get_crew(st.session_state.restaurant_id)
            if not rows:
                st.info(t("employees", lang))
            else:
                for row in rows:
                    crew_id, first_name, last_name, birthdate, status, contract_hours, function, department, notes, active = row
                    age = calculate_age(birthdate)
                    st.markdown(
                        f"""
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
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"🗑️ {t('delete', lang)} - {first_name} {last_name}", key=f"delete_crew_{crew_id}"):
                        delete_crew(crew_id)
                        st.success(f"✅ {t('deleted', lang)}")
                        st.rerun()

with tab_roster:
    st.header(f"📅🔍 {t('roster_check', lang)}")
    resto = selected_restaurant_banner(lang)
    if resto:
        c1, c2 = st.columns(2)
        with c1:
            show_card("📥", "Rooster importeren", "Hier komt de import van het roosterbestand.")
        with c2:
            show_card("🔍", "Controle uitvoeren", "Hier komt de bestaande wettelijke controlelogica.")
        c3, c4 = st.columns(2)
        with c3:
            show_card("⚠️", "Fouten bekijken", "Fouten worden naast de juiste rij getoond.")
        with c4:
            show_card("📄", "Gemarkeerde export", "De bestaande gemarkeerde Excel-export blijft hetzelfde.")
        st.info("Volgende fase: bestaande wettelijke controle en exportlogica integreren.")

with tab_reports:
    st.header(f"📊 {t('reports', lang)}")
    resto = selected_restaurant_banner(lang)
    if resto:
        c1, c2, c3 = st.columns(3)
        with c1:
            show_card("⚠️", "Overtredingen", "Overzicht van wettelijke fouten.")
        with c2:
            show_card("👶", "Minderjarigen", "Controle volgens leeftijd.")
        with c3:
            show_card("⏰", "Contracturen", "Controle voor vaste medewerkers.")
        st.info(t("coming_later", lang))
