import streamlit as st
import pandas as pd
from datetime import date
from database import init_db, get_restaurant, add_crew, get_crew, calculate_age, update_crew, delete_crew
from translations import t

st.set_page_config(page_title="Crew", page_icon="👥", layout="wide")
init_db()

if "lang" not in st.session_state:
    st.session_state.lang = "nl"
if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None

lang = st.session_state.lang

st.title(t("crew_database", lang))

if not st.session_state.restaurant_id:
    st.warning(t("select_restaurant", lang))
    st.stop()

restaurant = get_restaurant(st.session_state.restaurant_id)
if not restaurant:
    st.warning(t("select_restaurant", lang))
    st.stop()

st.success(f"{t('selected_restaurant', lang)}: {restaurant[1]}")

status_options = {
    "student": t("student", lang),
    "vast": t("fixed", lang),
    "flexi": t("flexi", lang),
    "interim": t("interim", lang),
}

tab_add, tab_overview, tab_edit = st.tabs([
    t("add_crew", lang),
    t("employees", lang),
    t("edit_restaurant", lang),
])

with tab_add:
    with st.form("add_crew_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input(t("first_name", lang))
            last_name = st.text_input(t("last_name", lang))
            birthdate = st.date_input(
                t("birthdate", lang),
                value=date(2000, 1, 1),
                min_value=date(1940, 1, 1),
                max_value=date.today(),
            )
            age = calculate_age(birthdate.isoformat())
            st.caption(f"{t('age_today', lang)}: {age} | {t('is_minor', lang)}: {t('yes', lang) if age < 18 else t('no', lang)}")

        with col2:
            status_label = st.selectbox(t("status", lang), list(status_options.values()))
            status = [k for k, v in status_options.items() if v == status_label][0]

            contract_hours = None
            if status == "vast":
                contract_hours = st.number_input(t("contract_hours", lang), min_value=1.0, max_value=60.0, step=0.5)

            function = st.text_input(t("function", lang))
            department = st.text_input(t("department", lang))
            active = st.checkbox(t("active", lang), value=True)
            notes = st.text_area(t("notes", lang))

        submitted = st.form_submit_button(t("save", lang), type="primary")

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
                st.success(t("employee_saved", lang))
                st.rerun()

with tab_overview:
    rows = get_crew(st.session_state.restaurant_id)
    if rows:
        data = []
        for row in rows:
            crew_id, first_name, last_name, birthdate, status, contract_hours, function, department, notes, active = row
            age = calculate_age(birthdate)
            data.append({
                "ID": crew_id,
                t("first_name", lang): first_name,
                t("last_name", lang): last_name,
                t("birthdate", lang): birthdate,
                t("age_today", lang): age,
                t("is_minor", lang): t("yes", lang) if age < 18 else t("no", lang),
                t("status", lang): status,
                t("contract_hours", lang): contract_hours,
                t("function", lang): function,
                t("department", lang): department,
                t("active", lang): t("yes", lang) if active else t("no", lang),
                t("notes", lang): notes,
            })
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info(t("employees", lang))

with tab_edit:
    rows = get_crew(st.session_state.restaurant_id)
    if not rows:
        st.info(t("employees", lang))
    else:
        crew_options = {f"{r[2]} {r[1]}": r for r in rows}
        selected_key = st.selectbox(t("employees", lang), list(crew_options.keys()))
        selected = crew_options[selected_key]

        with st.form("edit_crew_form"):
            crew_id, first_name, last_name, birthdate, status, contract_hours, function, department, notes, active = selected
            col1, col2 = st.columns(2)
            with col1:
                new_first_name = st.text_input(t("first_name", lang), value=first_name)
                new_last_name = st.text_input(t("last_name", lang), value=last_name)
                new_birthdate = st.date_input(t("birthdate", lang), value=date.fromisoformat(birthdate))
                age = calculate_age(new_birthdate.isoformat())
                st.caption(f"{t('age_today', lang)}: {age} | {t('is_minor', lang)}: {t('yes', lang) if age < 18 else t('no', lang)}")

            with col2:
                reverse_status_options = {v: k for k, v in status_options.items()}
                current_label = status_options.get(status, status)
                new_status_label = st.selectbox(
                    t("status", lang),
                    list(status_options.values()),
                    index=list(status_options.values()).index(current_label) if current_label in status_options.values() else 0,
                )
                new_status = reverse_status_options[new_status_label]

                new_contract_hours = None
                if new_status == "vast":
                    new_contract_hours = st.number_input(
                        t("contract_hours", lang),
                        min_value=1.0,
                        max_value=60.0,
                        step=0.5,
                        value=float(contract_hours or 38.0),
                    )

                new_function = st.text_input(t("function", lang), value=function or "")
                new_department = st.text_input(t("department", lang), value=department or "")
                new_active = st.checkbox(t("active", lang), value=bool(active))
                new_notes = st.text_area(t("notes", lang), value=notes or "")

            submitted = st.form_submit_button(t("save", lang))
            if submitted:
                update_crew(
                    crew_id=crew_id,
                    first_name=new_first_name,
                    last_name=new_last_name,
                    birthdate=new_birthdate.isoformat(),
                    status=new_status,
                    contract_hours=new_contract_hours,
                    function=new_function,
                    department=new_department,
                    notes=new_notes,
                    active=new_active,
                )
                st.success(t("saved", lang))
                st.rerun()

        if st.button(t("delete", lang), key=f"delete_crew_{selected[0]}"):
            delete_crew(selected[0])
            st.success(t("deleted", lang))
            st.rerun()
