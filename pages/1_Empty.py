import streamlit as st
import pandas as pd
import numpy as np

from deta import Deta
import os

#Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_USERS_BASE'))
pledges=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_PLEDGES_BASE'))
st.markdown("# Watch this space")
st.sidebar.markdown("# Empty Placeholder")

if not st.session_state['authentication_status'] :
    st.stop()
else:
    res = pledges.fetch(query={"player" : "Mason Bain"})
    max_index = res.count - 1
    st.subheader("Your pledges :")
    df = pd.DataFrame(res.items).drop(columns=['key', 'card_id'])
    with st.expander("Show Pledge Details"):
        st.write(df)
        with st.form("Pick the record by its index to display",clear_on_submit=True):
            update_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            show = st.form_submit_button("Show")
            if show:
                st.write(display[update_index])
    with st.expander("Update the status of my pledge"):

        with st.form("Pick the record by its index to update",clear_on_submit=True):
            update_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            status = st.radio(
                "What is the status of the pledge?",
                ('In Progress', 'Paid', 'Denied'))
            message = f"The pledge with id {res.items[update_idex]['card_id']} will be update to {status} status"
            st.write(message)
