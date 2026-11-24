# Project Memory

## Project

- Fictional restaurant: Pie in the Sky, Woodstock, Illinois.
- Repository: `sd70mac/mw_python_final_fa26`, branch `main`.
- Current deployed Streamlit app:
  <https://pie-in-the-sky-mwpythonfinalfa26-fd3b3pv7uevlcikoulhklz.streamlit.app/>
- Streamlit Cloud must run `streamlit_app.py`. `main.py` is the console ordering
  client; do not select it as the web entry point.

## Current behavior and architecture

- `menu.txt` and `dessert_menu.txt` are the source of menu categories, items,
  and prices.
- The Streamlit order page supports item selection, quantities, tea/coffee
  add-ons, an itemized order summary with unit and line prices, subtotal, and
  8.75% Woodstock sales tax.
- `st.session_state` holds the in-progress cart across Streamlit reruns.
- Completed orders are stored durably in Supabase when configured. The console
  and hosted web app use the same Supabase table. The local API and CSV remain
  development fallbacks; the Cloud app cannot reach the owner's localhost.
- The public page shows anonymized popular item combinations, not customer
  names or individual orders. The console can view recent orders.
- Order timestamps are timezone-aware and displayed in `America/Chicago`
  (CST/CDT); Supabase may return the same instants in UTC.
- The SQL migration is under `supabase/migrations/`. Supabase GitHub
  integration uses working directory `.` and the existing GitHub `main`
  production branch. Automatic preview branching is not needed for the free
  setup.
- Streamlit Cloud secrets are named `SUPABASE_URL` and `SUPABASE_SECRET_KEY`.
  The console uses `PIE_SUPABASE_URL` and `PIE_SUPABASE_KEY` locally. Never
  request or include the actual secret values in chat or project memory.

## Recent work completed

- The owner deployed the app successfully at the URL above.
- Added explicit Session State handling for the in-progress cart and a clear
  order action.
- Updated timestamps to Central Time and added tests for CST/CDT conversion.
- Added item prices and extended line prices to the Full Order section; the
  owner pushed this change to GitHub `main`.
- The owner keeps the Supabase secret in a password manager.

## Next session

- First check `git status`, recent commits, and the deployed app state; changes
  may have been pushed since this note was written.
- Ask what the owner wants to usability-test or improve next.
- If debugging deployment, check the exact Cloud error and confirm repository,
  branch `main`, entry point `streamlit_app.py`, and presence (not values) of
  both required Streamlit secrets.
- For order persistence issues, verify the `orders` table/migration and test
  with a harmless order only with the owner's permission. Never ask them to
  reveal or paste their Supabase secret key.
