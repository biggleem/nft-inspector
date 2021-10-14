import streamlit as st
import requests, json

endpoints = st.sidebar.selectbox("Endpoints", ['Assets', 'Events', 'Rarity'])

st.header(f"Open Sea NFT Inspector - {endpoints}")

st.sidebar.subheader("Filters")

collection = st.sidebar.text_imput("Collection")
owner = st.sidebar.text_imput("Owner")

if endpoints == 'Assets':
   
   params = {}

   if collection:
        params['collection'] = 'collection'
   if owner:
        params['owner'] = 'owner'
#     params = {
#     'collection': collection,
    
# }

r = requests.get("https://api.opensea.io/api/v1/assets", params=params)

st.write(r.json())