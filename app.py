import streamlit as st
from database import (
    init_db,
    get_restaurants,
    add_restaurant,
    update_restaurant,
    delete_restaurant,
    get_restaurant,
)
from translations import t

st.set_page_config(page_title="RestoCheck", page_icon="✅", layout="wide")
init_db()

if "lang" not in st.session_state:
    st.session_state.lang = "nl"

if "restaurant_id" not in st.session_state:
    st.session_state.restaurant_id = None

lang_labels = {
    "nl": "Nederlands",
    "fr": "Français",
    "en": "English",
}

with st.sidebar:
    st.session_state.lang = st.selectbox(
        "Taal / Langue / Language",
        options=list(lang_labels.keys()),
        format_func=lambda x: lang_labels[x],
        index=list(lang_labels.keys()).index(st.session_state.lang),
    )

    st.divider()
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Crew.py", label="👥 Crew")
    st.page_link("pages/2_Roostercontrole.py", label="📅 Roostercontrole")
    st.page_link("pages/3_Rapporten.py", label="📊 Rapporten")

lang = st.session_state.lang

st.title(t("app_title", lang))

restaurants = get_restaurants(active_only=False)

st.header(t("select_restaurant", lang))

if not restaurants:
    st.info(t("no_restaurant", lang))
else:
    options = {
        f"{name} {'✅' if active else '⛔'}": rid
        for rid, name, address, active in restaurants
    }

    selected_label = st.selectbox(
        t("select_restaurant", lang),
        list(options.keys()),
    )

    if st.button(t("open_restaurant", lang), type="primary"):
        st.session_state.restaurant_id = options[selected_label]
        st.success(f"{t('selected_restaurant', lang)}: {selected_label}")

if st.session_state.restaurant_id:
    resto = get_restaurant(st.session_state.restaurant_id)
    if resto:
        st.success(f"{t('selected_restaurant', lang)}: {resto[1]}")

st.divider()
st.header(t("restaurant_management", lang))

tab_add, tab_edit, tab_delete = st.tabs(
    [
        t("add_restaurant", lang),
        t("edit_restaurant", lang),
        t("delete_restaurant", lang),
    ]
)

with tab_add:
    with st.form("add_restaurant_form"):
        name = st.text_input(t("restaurant_name", lang))
        address = st.text_input(t("address", lang))
        active = st.checkbox(t("active", lang), value=True)

        submitted = st.form_submit_button(t("save", lang))

        if submitted:
            if name.strip():
                try:
                    add_restaurant(name, address, active)
                    st.success(t("saved", lang))
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            else:
                st.error(t("restaurant_name", lang))

with tab_edit:
    if restaurants:
        edit_map = {
            name: rid
            for rid, name, address, active in restaurants
        }

        edit_name = st.selectbox(
            t("edit_restaurant", lang),
            list(edit_map.keys()),
            key="edit_restaurant_select",
        )

        selected = get_restaurant(edit_map[edit_name])

        if selected:
            with st.form("edit_restaurant_form"):
                new_name = st.text_input(
                    t("restaurant_name", lang),
                    value=selected[1],
                )

                new_address = st.text_input(
                    t("address", lang),
                    value=selected[2] or "",
                )

                new_active = st.checkbox(
                    t("active", lang),
                    value=bool(selected[3]),
                )

                submitted = st.form_submit_button(t("save", lang))

                if submitted:
                    update_restaurant(
                        selected[0],
                        new_name,
                        new_address,
                        new_active,
                    )
                    st.success(t("saved", lang))
                    st.rerun()
    else:
        st.info(t("no_restaurant", lang))

with tab_delete:
    if restaurants:
        delete_map = {
            name: rid
            for rid, name, address, active in restaurants
        }

        delete_name = st.selectbox(
            t("delete_restaurant", lang),
            list(delete_map.keys()),
            key="delete_restaurant_select",
        )

        confirm = st.checkbox(t("confirm_delete", lang))

        if st.button(t("delete", lang), disabled=not confirm):
            delete_restaurant(delete_map[delete_name])

            if st.session_state.restaurant_id == delete_map[delete_name]:
                st.session_state.restaurant_id = None

            st.success(t("deleted", lang))
            st.rerun()
    else:
        st.info(t("no_restaurant", lang))

st.divider()
st.subheader("Volgende stap")
st.write(
    "Kies links in het menu voor **👥 Crew** om medewerkers toe te voegen."
)
