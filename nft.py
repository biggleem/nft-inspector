import streamlit as st
import requests, json
import pandas as pd
from web3 import Web3

endpoints = st.sidebar.selectbox("Endpoints", ['Assets', 'Events', 'Rarity'])

st.header(f"Open Sea NFT Inspector - {endpoints}")

# st.sidebar.subheader("Filters")

# collection = st.sidebar.text_input("Collection")
# owner = st.sidebar.text_input("Owner")

if endpoints == 'Assets':
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner")
    collection = st.sidebar.text_input("Collection")
    params = {'owner': owner}
    if collection:
        params['collection'] = collection
    
    r = requests.get('https://api.opensea.io/api/v1/assets', params=params)

    assets = r.json()['assets']
    for assets in assets:
        # render_asset(asset)
    
    st.subheader("Raw JSON Data")
    st.write(r.json())

    if endpoints == 'Rarity':
        with open(assets.json) as f:
            data = json.loads(f.read())
            asset_rarities = []



# if endpoints == 'Assets':

#    params = {}

#    if collection:
#         params['collection'] = collection
#    if owner:
#         params['owner'] = owner
# r = requests.get("https://api.opensea.io/api/v1/assets", params=params)

# response = r.json()

# for asset in response["assets"]:
#     if asset['name']:
#         st.write(asset['name'])
#     else:
#         st.write(f"{asset['collection']['name']} #{asset['token_id']}")
#     if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
#         st.video(asset['image_url'])
#     else:
#         st.image(asset['image_url'])


if endpoints == 'Events':
    collection = st.sidebar.text_input("Collection")
    asset_contract_address = st.sidebar.text_input("Contact Address")
    token_id = st.sidebar.text_input("Token ID")
    event_type = st.sidebar.selectbox("Event Type", ['offer_entered', 'cancelled', 'bid_withdrawn', 'transfer', 'approve'])

    params = {}

    if collection:
        params['collection_slug'] = collection
    if asset_contract_address:
        params['asset_contract_address'] = asset_contract_address
    if token_id:
        params['token_id'] = token_id
    if event_type:
        params['event_type'] = event_type
    
    r = requests.get('https://api.opensea.io/api/v1/events', params=params)

    events = r.json()
    
    event_list = []

    for event in events['asset_events']:
        if event_type == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']), 'ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']

            event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['collection']['name'], event['asset']['token_id']])

    df = pd.DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])
    st.write(df)

    st.write(events)
 
    st.write(r.json())