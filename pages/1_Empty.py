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
    with st.expander("Update the status of my pledge"):
        res = pledges.fetch(query={"player" : "Mason Bain"})
        max_index = res.count - 1
        st.subheader("Your pledges :")
        st.dataframe(res.items)
        with st.form("Pick the record by its index to update",clear_on_submit=True):
            update_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            st.write(res.items[update_index])
