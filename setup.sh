mkdir -p ~/.streamlit/
echo "[theme]
primaryColor='#6eb52f'
backgroundColor='#f0f0f5'
secondaryBackgroundColor='#e0e0ef'
textColor='#262730'
font='sans serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml