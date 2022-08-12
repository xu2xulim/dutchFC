import streamlit as st
import pandas as pd
import numpy as np

from deta import Deta
import os

#Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_USERS_BASE'))
pledges=Deta(os.environ.get('DETA_PROJECT_ID')).Base('dfc_pledge_93')
#st.markdown("# Watch this space")
#st.sidebar.markdown("# Empty Placeholder")

if not st.session_state['authentication_status'] :
    st.stop()
else:
    res = pledges.fetch(query={"player" : st.session_state['name'], "status?ne" : "Collected"})
    #res = pledges.fetch()
    max_index = res.count - 1
    st.subheader("Your pledges :")
    df = pd.DataFrame(res.items).drop(columns=['key'])
    refresh = st.button("Refresh")
    st.write(df)
    if refresh :
        st.experimental_rerun()
    with st.expander("Show Pledge Details"):

        with st.form("Pick the record by its index to display",clear_on_submit=True):
            show_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            show = st.form_submit_button("Show")
            if show:
                selected_key = res.items[show_index]['key']
                st.write("Pledger :", res.items[show_index]['pledger'])
                st.write("Email :", res.items[show_index]['email'])
                #st.write("Address :", res.items[show_index]['address'])
                st.write("Phone :", res.items[show_index]['phone'])
                st.write("Pledge Per Point :", res.items[show_index]['pledgepp'])
                st.write("Maximum Amount :", res.items[show_index]['max_amt'])
                st.write("Phone :", res.items[show_index]['phone'])
                try :
                    st.write("Status :", res.items[show_index]['status'])
                except:
                    st.write("Status :", "To be collected")

    with st.expander("Update the status of my pledge"):

        with st.form("", clear_on_submit=True):

            st.write("Updating for pledger", res.items[show_index]['pledger'])

            update_status = st.selectbox("What is the status of the pledge?", ('To be collected', 'Collected', 'Denied'))

            submit = st.form_submit_button("Submit")

            if submit:
                st.write("The pledge from ", res.items[show_index]['pledger'], " will be update to" , update_status, " status.")
                update = {"status" : update_status}
                pledges.update(update, selected_key)


    with st.expander("Marked Collected"):
        res_collected = pledges.fetch(query={"player" : st.session_state['name'], "status" : "Collected"})
        if res_collected.count !=0:
            df_collected = pd.DataFrame(res_collected.items).drop(columns=['key'])
            st.write(df_collected) #
        else:
            st.write("Nothing to show at this point.")
