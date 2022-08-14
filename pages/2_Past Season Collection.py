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
    df = pd.DataFrame(res.items)
    refresh = st.button("Refresh")
    st.write(df)
    if refresh :
        st.experimental_rerun()
    st.session_state['pledger_key'] = None
    with st.expander("Show Pledge Details"):
        #st.session_state['update'] = "False"
        action = "No"
        with st.form("Pick the record by its index to display",clear_on_submit=True):
            show_index = st.number_input("Index", min_value=0, max_value=max_index, step=1)
            show = st.form_submit_button("Show")
            if st.session_state['pledger_key'] != None:
                collected = st.form_submit_button("Update this pledge to Collected")
            if show:
                st.write("Pledger Record Key :", res.items[show_index]['key'], "  ** Copy and Paste ")
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
                st.session_state['pledger_key'] = res.items[show_index]['key']
            if collected and st.session_state['pledger_key'] != None :
                updated = pledges.update({"status" : "Collected"}, st.session_state['pledger_key'])



"""    if st.session_state['update'] == True:
        with st.expander("Update the status of pledge"):

            with st.form("Select the new status", clear_on_submit=True):

                pledge4update = pledges.get(st.session_state['pledger_key'])
                st.write("You are updating the pledge status of pledger ", pledge4update['pledger'])
                update_status = st.radio(
                    "What is the status of the pledge?",
                    ('To be collected', 'Collected', 'Denied'))

                submit = st.form_submit_button("Submit")

                if submit:
                    st.write("Updating .....")
                    update = {"status" : update_status}
                    st.write(st.session_state['pledger_key'])
                    st.write(update_status)
                    st.stop()
                    updated = pledges.update(update, st.session_state['pledger_key'])
                    st.write("The pledge from ", pledge4update['name'], " will be update to" , update_status, " status.")"""


    with st.expander("Marked Collected"):
        res_collected = pledges.fetch(query={"player" : st.session_state['name'], "status" : "Collected"})
        if res_collected.count !=0:
            df_collected = pd.DataFrame(res_collected.items).drop(columns=['key'])
            st.write(df_collected) #
        else:
            st.write("Nothing to show at this point.")
