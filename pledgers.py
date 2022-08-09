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


@st.cache(suppress_st_warning=True)
def auth_init():

    res = Users.fetch(query=None, limit=100, last=None)
    cd = {"usernames" : {} }
    if res:
        for x in res.items :
            cd['usernames'][x['username']] = {'name' : x['name'], 'password' : x['hash_password'], 'email' : x['email']}

        #usernames.append(x['username'])
        #hashed_passwords.append(x['hash_password'])

    return cd

@st.cache(suppress_st_warning=True)
def get_card_json (url):

    res = requests.post('https://cs0kji.deta.dev/url2json', json={"url" : url})
    if res.status_code == 200 :
        return res.json()
    else:
        return {}

Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_USERS_BASE'))
Users=Deta(os.environ.get('DETA_PROJECT_ID')).Base(os.environ.get('DFC_PLEDGES_BASE'))

with st.sidebar:
    st.title("DutchFC Pledges")
    credentials = auth_init()

    if credentials:
        authenticator = stauth.Authenticate(credentials,
            'dfc_stauth', os.environ.get('DFC_USERS_SIGNATURE'), cookie_expiry_days=30)
        st.info("This application is secured by Streamlit-Authenticator.")
    else:
        st.session_state['authentication_status'] = False
        st.info("Administrator setup is required.")

    name, authentication_status, username = authenticator.login('Login', 'sidebar')
    st.session_state['authentication_status'] = authentication_status

    if st.session_state['authentication_status']:
        authenticator.logout('Logout', 'main')
        st.write('Welcome *%s*' % (st.session_state['name']))

        res = Users.fetch(query={"name" : name, "username" : username}, limit=None, last=None)
        if len(res.items) == 1:
            user = Users.get(res.items[0]["key"])
            card_dict = {}
            if "shared_cards" in user.keys():
                for url in user["shared_cards"] :
                    card_json = get_card_json(url)
                    card_dict[card_json['name']] = card_json['id']

        option = st.selectbox(
            'Select the card you like to see',
            options=list(card_dict.keys()))

        st.write('You selected:', option)
        st.session_state['card_id'] = card_dict[option]
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
                    Users.put({'name' : name, 'username' : username, 'hash_password' : stauth.Hasher([password]).generate()[0]})

        with st.expander("Admin setup"):
            st.warning("This form is used by the administrator to attach card urls to a username. An admin secret is required for the update.")
            with st.form("Enter the card url to be shared with the user", clear_on_submit=True):
                username = st.text_input("Username")
                url = st.text_input("Card URL")
                admin_secret = st.text_input("Admin Secret", type="password")

                submit = st.form_submit_button("Submit")

                if submit and admin_secret == os.environ.get('DFC_USERS_SIGNATURE'):
                    users = Users.fetch(query={"username" : username}, limit=None, last=None)
                    if len(users.items) != 1 :
                        st.write("User is not found")
                    else:
                        st.write(users.items[0]["key"])
                        user = Users.get(users.items[0]["key"])
                        try :
                            shared_cards = user['shared_cards']
                        except:
                            shared_cards = []
                        if url in shared_cards :
                            st.write("Card with url {} is already shared with {}".format(url, username))
                        else:
                            shared_cards.append(url)
                            Users.update({"shared_cards" : shared_cards }, user["key"])
                            st.write("Card with url {} is shared with {}".format(url, username))

if not st.session_state['authentication_status']  :
    st.stop()
refresh = st.button("Refresh")

if refresh :
    st.experimental_rerun()
st.stop()
"""if 'card_id' in st.session_state:
    card_id = st.session_state['card_id']


res = requests.post('https://cs0kji.deta.dev/card_json', json={"card_id" : card_id})
#res = requests.post('https://70297.wayscript.io/email2board', json={"card_id" : card_id})

if res.status_code == 200 :
    card_json=res.json()

else:
    st.stop()

if card_json['idAttachmentCover'] == None and card_json['manualCoverAttachment'] == True :
    request = urllib.request.Request(card_json['cover']['scaled'][-1]['url'])
    webUrl  = urllib.request.urlopen(request)

    st.image(webUrl.read())
else:
    res = requests.post('https://cs0kji.deta.dev/get_attachment', json={"url" : card_json['cover']['scaled'][-1]['url']})
    if res.status_code == 200:
        st.image(res.content)

st.header(card_json['name'])

with st.expander("Swagger"):
    link = '[Demo](https://f0w9hg.deta.dev/docs)'
    st.markdown(link, unsafe_allow_html=True)

with st.expander("Open to see card labels"):
    lbl_head = '''<p style="margin: 0;"><span style="background-color:rgb(252, 252, 252);"><span class="ql-cursor">﻿</span><span class="cl-trello-card-labels">'''
    lbl_tail = '''</span></span></p>'''
    for lbl in card_json['labels']:
        lbl_name = lbl['name']
        if lbl['name'] == "":
            lbl_name = lbl['color']
        itm = '''<b style="color: {}; margin-right: 1.5em;">■ {}</b>'''.format(lbl['color'], lbl_name)
        lbl_head = lbl_head + itm

    components.html(lbl_head + lbl_tail)

with st.expander("Open to see card start and due status"):
    #st. write(card_json)
    dates = {}
    dates['Start'] = parse(card_json['start']).astimezone(tz).strftime('%Y-%m-%d')
    dates['Due'] = parse(card_json['due']).astimezone(tz).strftime('%Y-%m-%d %H:%M')
    dates['Completed?'] = card_json['dueComplete']

    st.json(dates)


with st.expander("Open to read card description"):
    st.markdown(card_json['desc'], unsafe_allow_html=False)

with st.expander("Open to inspect custom fields on card"):
    res = requests.post('https://cs0kji.deta.dev/card_customfields', json={"card_id" : card_id})
    if res.status_code == 200 :
        cf_list = res.json()['customfields']
        st.write(cf_list)
        ix = 0
        for x in cf_list:
            if x['Type'] == "date" and x['Value'] != "":
                #if x['Value'][-1] == "Z" and x['Value'].index("T") == 10:
                    #try:
                cf_list[ix]['Value'] = parse(x['Value']).astimezone(tz).strftime('%Y-%m-%d %H:%M')
                    #except:
                        #pass


            ix += 1

        st.json(cf_list)

with st.expander("Open to see location on card"):
    res = requests.post('https://cs0kji.deta.dev/card_location', json={"card_id" : card_id})
    if res.status_code == 200 :
        result=res.json()
        if 'latitude' in result['coordinates'].keys() and 'longitude' in result['coordinates'].keys() :
            st.json(result)
            lat = result['coordinates']['latitude']
            lon = result['coordinates']['longitude']
            #st.json(res.json())
            #location = pd.DataFrame(res.json()['coordinates'], columns=['lat', 'lon'])
            #st.map(data=location, zoom=20, use_container_width=True)
            m = folium.Map(location=[lat, lon], zoom_start=16)
            # add marker for Liberty Bell
            tooltip = result['address']
            folium.Marker(
                [lat, lon], popup=result['locationName'], tooltip=tooltip
                ).add_to(m)

                # call to render Folium map in Streamlit
            folium_static(m, width=660, height=385)

with st.expander("Open to see status of checklists on card"):

    res = requests.post('https://cs0kji.deta.dev/card_checklistitems', json={"card_id" : card_id})
    if res.status_code == 200 :
        checklist_d = res.json()
        for cl in checklist_d.keys():
            st.write(cl)
            items = pd.DataFrame(checklist_d[cl]).fillna("Not Available")
            items["state"].replace({"complete": "✅", "incomplete": "❌"}, inplace=True)
            ix = 0
            for itm in items["due"] :
                if itm != None:
                    try:
                        items["due"].iloc[ix] = parse(itm).astimezone(tz).strftime('%Y-%m-%d')
                    except:
                        pass
                ix += 1

            st.dataframe(items)

with st.expander("Open to see images of attachments"):
    columns = st.columns(5)
    ix = 0
    res = requests.post('https://cs0kji.deta.dev/card_attachments', json={"card_id" : card_id})
    if res.status_code == 200 :
        for attach in res.json()['attachments']:
            ext = attach['fileName'].split(".")[-1]
            if (ext == 'jpg' or ext == 'png' or ext == 'jpeg') and attach['id'] != card_json['idAttachmentCover'] and ix <5:
                res = requests.post('https://cs0kji.deta.dev/get_attachment', json={"url" : attach['url']})

                if res.status_code == 200:
                    with columns[ix]:
                        columns[ix].image(res.content)
                    ix += 1
                else:
                    st.warning(res.status_code)
"""
