# Pie in the Sky

A Streamlit ordering page and console client for a fictional restaurant in
Woodstock, Illinois. Both clients use the same local order API, which reads the
menu from `menu.txt` and `dessert_menu.txt` and saves submitted orders in
`orders.csv`. The Streamlit page displays menu prices, calculates 8.75% sales
tax, supports quantities and tea/coffee add-ons, and allows saved orders to be
reordered.

## Run locally

1. Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv` and `source .venv/bin/activate`
   - Windows PowerShell: `py -m venv .venv` and `.venv\Scripts\Activate.ps1`
2. Install the web app dependency with `python -m pip install -r requirements.txt`.
3. In a terminal, start the shared API: `python api_server.py`.
4. In a second terminal, activate the same environment and run
   `streamlit run streamlit_app.py`.
5. To use the console ordering client, run `python main.py` in another terminal.

The web page and console show orders saved through either client. The API binds
to `127.0.0.1`, so it is only available on the same computer. The kiosk draft's
prices are included in parentheses in the menu files. Older menu items without
a listed price remain available for display but cannot be submitted until a
price is assigned.

Run the shared menu and order tests with `python -m unittest discover -s tests`.
