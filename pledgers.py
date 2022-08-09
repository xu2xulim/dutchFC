import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
#from streamlit_folium import folium_static
#import folium

import os
from datetime import datetime
from deta import Deta
import json
import requests

import urllib.request
import urllib.parse
#from trello import TrelloClient, List
from dateutil.parser import parse
from datetime import datetime
import pytz
tz = pytz.timezone('Asia/Singapore')

Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_USERS_BASE'))
pledges=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_PLEDGES_BASE'))

#@st.cache(suppress_st_warning=True)
def auth_init():

    res = Users.fetch()

    cd = {"usernames" : {} }
    if res.count == 0:
        pass
    else:
        for x in res.items :
            cd['usernames'][x['username']] = {'name' : x['name'], 'password' : x['hash_password'], 'email' : x['email']}
            #hashed_passwords.append(x['hash_password'])
    return cd

with st.sidebar:
    st.title("Dutch FC Pledges")

    credentials = auth_init()

    if credentials['usernames'] != {}:
        authenticator = stauth.Authenticate(credentials,
            'dfc_stauth', os.environ.get('DFC_USERS_SIGNATURE'), cookie_expiry_days=30)
        st.info("This application is secured by Streamlit-Authenticator.")

    else:
        st.session_state['authentication_status'] = False
        st.info("Administrator setup is required.")

    #st.session_state['authentication_status'] = authentication_status
    name, authentication_status, username = authenticator.login('Login', 'sidebar')
    st.session_state['authentication_status'] = authentication_status

    if st.session_state['authentication_status']:
        authenticator.logout('Logout', 'main')
        st.write('Welcome *%s*' % (st.session_state['name']))

    elif st.session_state['authentication_status'] == False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] == None:
        st.warning('Please enter your username and password')


    if not st.session_state['authentication_status']:
        with st.expander("Register"):
            st.warning("This form is for user self registration. The registration data is kept in a Deta Base.")
            with st.form("Fill in your name, your preferred username and password", clear_on_submit=True):
                name = st.text_input("Name")
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                username_unique = Users.fetch(query={"username" : username})

                submit = st.form_submit_button("Submit")
                if username_unique.count == 0:
                    pass
                else:
                    st.write("The username : {} has been used, please use another preferred username.".format(username))
                    st.stop()

                if submit:
                    Users.put({'name' : name, 'username' : username, 'hash_password' : stauth.Hasher([password]).generate()[0], 'email' : email})



if not st.session_state['authentication_status']  :
    st.stop()
refresh = st.button("Refresh")
if refresh :
    st.experimental_rerun()

res = pledges.fetch(query={"player" : name})

pledges = {}
for itm in res.items:
    if itm['program'] not in pledges.keys():
        pledges[itm['program']] = []
    pledges[itm['program']].append(f"Pledge for \${itm['points']} per point up to \${itm['amount']} from {itm['pledger']}")

for pl in pledges.keys() :
    with st.expander(pl):
        for row in pledges[pl] :
            st.write(row)
