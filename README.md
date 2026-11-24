# Pie in the Sky

A Streamlit ordering page and console client for a fictional Woodstock,
Illinois restaurant. Both clients read the menu from `menu.txt` and
`dessert_menu.txt`. For hosted use, the Streamlit app and console share orders
through Supabase; the local HTTP API and CSV file remain available for
development.

## Local development

1. Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv` and `source .venv/bin/activate`
   - Windows PowerShell: `py -m venv .venv` and `.venv\Scripts\Activate.ps1`
2. Install Streamlit with `python -m pip install -r requirements.txt`.
3. Start the local order API in one terminal: `python api_server.py`.
4. In another terminal, activate the environment and run
   `streamlit run streamlit_app.py`.
5. To use the console client, run `python main.py` in another terminal.

## Host the web app and share orders

1. Create a Supabase project on the Free plan.
2. In Supabase **Project Settings → Integrations → GitHub Integration**, use
   this repository and set **Working directory** to `.` (the `supabase/` folder
   is at the repository root). Turn on **Deploy to production** and use the
   existing GitHub branch `main` as the production branch. Do not enable preview
   branching; that is the Pro feature shown in the screenshot.
3. The schema migration is
   [`20261124005000_create_orders.sql`](./supabase/migrations/20261124005000_create_orders.sql).
   Push it to GitHub `main`; Supabase will apply pending migrations to the
   production project. Alternatively, paste that file into the Supabase SQL
   Editor and run it manually.
4. In Streamlit Community Cloud, select this repository, branch `main`, and
   set **Main file path** to `streamlit_app.py` (not `main.py`).
5. In the app's Streamlit Cloud settings, add these secrets:

   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_SECRET_KEY = "sb_secret_..."
   ```

6. Keep the Supabase secret key private. Do not commit it or put it in
   browser-side code. The app uses it only in the Streamlit server runtime.
7. To let local Streamlit use the same hosted orders, create the ignored file
   `.streamlit/secrets.toml` with the same two TOML entries shown above.
8. To let the console use the same hosted orders, set `PIE_SUPABASE_URL` and
   `PIE_SUPABASE_KEY` in the console's local environment to the same project
   URL and secret key. Do not set these variables in the public GitHub
   repository.
9. Push the latest app code and menu files to the selected GitHub branch so
   Streamlit Cloud deploys the current version.

With Supabase configured, the Streamlit app and console read and write the
same durable order records; do not start `api_server.py` for that mode. Without
Supabase credentials, both clients use the local API and `orders.csv`. The
public page shows anonymous popular item combinations, while full customer
order details remain private to the restaurant. The console displays the 20
most recent customer orders. The Streamlit order currently being assembled
is kept in `st.session_state` across reruns; placing an order saves it to
Supabase (or the local API in development), so it remains available after the
browser session ends.

Menu items without a listed price cannot be ordered. The page calculates
Woodstock sales tax at 8.75%. Order timestamps are timezone-aware and displayed
in the `America/Chicago` time zone (CST/CDT); Supabase may return the same
instants in UTC, which the console converts for display.

Run the tests with `python -m unittest discover -s tests`.
