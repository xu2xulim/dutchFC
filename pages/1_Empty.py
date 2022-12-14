import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from deta import Deta
import os

#Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_USERS_BASE'))
pledges=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_PLEDGES_BASE'))
st.markdown("# Watch this space")
st.sidebar.markdown("# Empty Placeholder")

if not st.session_state['authentication_status'] :
    st.stop()
else:
    res = pledges.fetch(query={"player" : st.session_state['name']})
    #res = pledges.fetch()
    max_index = res.count - 1
    st.subheader("Your pledges :")
    df = pd.DataFrame(res.items).drop(columns=['key', 'card_id'])
    with st.expander("Show Pledge Statistics"):
        chart_data = pd.DataFrame(
            np.random.randn(50, 3),
            columns=["a", "b", "c"])

        st.bar_chart(chart_data)

    with st.expander("Show Pledge Details"):
        st.write(df)
        with st.form("Pick the record by its index to display",clear_on_submit=True):
            show_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            show = st.form_submit_button("Show")
            if show:
                st.write("Pledger :", res.items[show_index]['pledger'])
                st.write("Email :", res.items[show_index]['email'])
                st.write("Address :", res.items[show_index]['address'])
                st.write("Phone :", res.items[show_index]['phone'])
                st.write("Pledge Per Point :", res.items[show_index]['pledgepp'])
                st.write("Maximum Amount :", res.items[show_index]['max_amt'])
                st.write("Phone :", res.items[show_index]['phone'])
                try :
                    st.write("Status :", res.items[show_index]['status'])
                except:
                    st.write("Status :", "To be implemented")

    with st.expander("Update the status of my pledge"):

        with st.form("Pick the record by its index to update",clear_on_submit=True):
            update_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            status = st.radio(
                "What is the status of the pledge?",
                ('In Progress', 'Paid', 'Denied'))
            submit = st.form_submit_button("Submit")
            if submit:
                st.write("The pledge from ", res.items[update_index]['pledger'], " will be update to" , status, " status.")
