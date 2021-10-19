from numpy import inexact, number
import streamlit as st
import requests, json, math
from web3 import Web3
import pandas as pd
from PIL import Image
import numpy as np

if not st.session_state.get("owner"):st.session_state.owner = ""
if not st.session_state.get("collection"):st.session_state.collection = ""
if not st.session_state.get('assets_page'):st.session_state.assets_page = 1
if not st.session_state.get('rarity_page'):st.session_state.rarity_page = 1
if not st.session_state.get('order_by'):st.session_state.order_by = "sale_date"
if not st.session_state.get('order_direction'):st.session_state.order_direction = "asc"

    

image = Image.open('images/nft-inspector-logo.gif')
st.sidebar.image(image, caption='Inspect any OpenSea.io NFT collection.')
st.sidebar.header("OpenSea API Endpoints")
endpoint_choices = ['Assets', 'Events', 'Rarity']
endpoint = st.sidebar.selectbox("Choose an Endpoint", endpoint_choices)

st.title(f"OpenSea NFT Inspector - {endpoint}")

def render_asset(asset):
    if asset['name'] is not None:
        name = asset['name']
        st.subheader(f"[{asset['name']}]({asset['permalink']})")
    else:
        name = f"[{asset['collection']['name']} #{asset['token_id']}]({asset['permalink']})"
        st.subheader(name)


    if asset['description'] is not None:
        st.write(asset['description'])
    else:
        st.write(asset['collection']['description'])

    if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
        st.video(asset['image_url'])
    elif asset['image_url'].endswith('svg'):
        svg = requests.get(asset['image_url']).content.decode()
        st.image(svg)
    elif asset['image_url']:
        # st.image(asset['image_url'])
        st.markdown(f"[![image]({asset['image_url']})]({asset['permalink']})")

@st.cache
def get_events(params):
    events = []
    for page in range(15):
        params['offset'] = page * 20
        r = requests.get('https://api.opensea.io/api/v1/events', params=params)
        events += r.json()['asset_events']
    return events

if endpoint == 'Events':
    collection = st.sidebar.text_input("Collection Slug",st.session_state.collection)
    asset_contract_address = st.sidebar.text_input("Contract Address")
    token_id = st.sidebar.text_input("Token ID")
    event_type = st.sidebar.selectbox("Event Type", ['offer_entered', 'cancelled', 'bid_withdrawn', 'transfer', 'approve'])
    params = {}
    if collection:
        params['collection_slug'] = collection
        st.session_state["collection"] = collection
    if asset_contract_address:
        params['asset_contract_address'] = asset_contract_address
    if token_id:
        params['token_id'] = token_id
    if event_type:
        params['event_type'] = event_type

    events = get_events(params)

    event_list = []
    for event in events:
        if event_type == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']), 'ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']

            event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['collection']['name'], event['asset']['token_id']])
    if not len(event_list):
        st.subheader("No result.")
    df = pd.DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])

    # df['time']= pd.to_datetime(df['time'],infer_datetime_format=True)
    new = df[['bid_amount',"time"]].copy()
    new = new.set_index("time")
    st.line_chart(new)  

    st.write(df)

    # st.subheader("Raw JSON Data")
    # st.write(events)

@st.cache
def get_assets(owner, collection, page, order_by, order_direction):
    params = {'owner': owner}
    params['collection'] = collection     
    params['order_by'] = order_by     
    params['order_direction'] = order_direction     
    params['offset'] = (page-1) * 20   
    r = requests.get('https://api.opensea.io/api/v1/assets', params=params)
    return r.json()['assets']

def update(key,value):
    st.session_state[key] = value
    page_text.subheader(f'Page {st.session_state.assets_page}')

order_by_list = ["token_id", "sale_date" , "sale_count", "sale_price"]

if endpoint == 'Assets':
    page,_,dir,by = st.columns([4,7,4,4])
    with dir:
        order_direction = st.selectbox("",options=["asc","desc"])
        st.session_state.order_direction = order_direction
    with by:
        order_by = st.selectbox("",options=order_by_list, index = order_by_list.index(st.session_state.order_by))
        st.session_state.order_by = order_by
    page_text = page.empty()
    page_text.subheader(f'Page {st.session_state.assets_page}')
    
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner Address",st.session_state.owner)
    st.session_state.owner= owner
    collection = st.sidebar.text_input("Collection",st.session_state.collection)
    if collection != st.session_state.collection:
        update("assets_page",1)
    st.session_state.collection = collection

    assets = get_assets(owner, collection, st.session_state.assets_page, st.session_state.order_by, st.session_state.order_direction)
    for asset in assets:                
        render_asset(asset)

    _,left,m1,m2,right,_ = st.columns([3,2,2,2,2,3])
    page_numbers = list(range(1,st.session_state.assets_page+100))
    m1.selectbox('',options=page_numbers, index=page_numbers.index(st.session_state.assets_page), key="asset_select_page")
    m2.button("Go",on_click=update, args=("assets_page",st.session_state.asset_select_page))
    if st.session_state.assets_page > 1:
        prev_btn = left.button("prev",on_click=update,args=("assets_page",st.session_state.assets_page - 1))
    else:
        left.empty()
    next_btn = right.button("next",on_click=update,args=("assets_page",st.session_state.assets_page + 1))
    
    if not len(assets):
        st.subheader("No result.")
    
    # st.subheader("Raw JSON Data")
    # st.write(r.json())

if endpoint == 'Rarity':
    page,_,dir,by = st.columns([4,7,4,4])
    with dir:
        order_direction = st.selectbox("",options=["asc","desc"])
        st.session_state.order_direction = order_direction
    with by:
        order_by = st.selectbox("",options=order_by_list, index = order_by_list.index(st.session_state.order_by))
        st.session_state.order_by = order_by

    page_text = page.empty()
    page_text.subheader(f'Page {st.session_state.assets_page}')

    asset_rarities = []
    owner = st.session_state["owner"]
    collection = st.session_state["collection"]
    assets = get_assets(owner, collection, st.session_state.rarity_page, st.session_state.order_by, st.session_state.order_direction)
    for asset in assets:
        asset_rarity = 1

        for trait in asset['traits']:
            trait_rarity = trait['trait_count'] / 8888
            asset_rarity *= trait_rarity

        asset_rarities.append({
            'token_id': asset['token_id'],
            'name': f"{asset['collection']['name']} #{asset['token_id']}",
            'description': asset['description'],
            'rarity': asset_rarity,
            'traits': asset['traits'],
            'image_url': asset['image_url'],
            'collection': asset['collection'],
            'permalink': asset['permalink']
        })

    assets_sorted = sorted(asset_rarities, key=lambda asset: asset['rarity']) 

    for asset in assets_sorted[:20]:
        render_asset(asset)
        st.subheader(f"{len(asset['traits'])} Traits")
        for trait in asset['traits']:
            st.write(f"{trait['trait_type']} - {trait['value']} - {trait['trait_count']} have this")

    _,left,m1,m2,right,_ = st.columns([3,2,2,2,2,3])
    page_numbers = list(range(1,st.session_state.rarity_page+100))
    m1.selectbox('',options=page_numbers, index=page_numbers.index(st.session_state.rarity_page), key="rarity_select_page")
    m2.button("Go",on_click=update, args=("rarity_page",st.session_state.rarity_select_page))
    if st.session_state.rarity_page > 1:
        prev_btn = left.button("prev",on_click=update,args=("rarity_page",st.session_state.rarity_page - 1))
    else:
        left.empty()
    next_btn = right.button("next",on_click=update,args=("rarity_page",st.session_state.rarity_page + 1))

    if not len(assets):
        st.subheader("No result.")

st.markdown(
"""
<style> 
    a {
        color: inherit !important; 
        text-decoration: inherit; 
    }
    [tabindex="0"] > .block-container{
        padding:20px 50px 10px 40px;        
    }
    [data-testid="stHorizontalBlock"]{
        align-items: center;
    }
    [tabindex="0"] label{
        display:none
    }
    header {visibility: hidden;}
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)