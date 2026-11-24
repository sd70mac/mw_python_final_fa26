# Reflection

## What went well

- We started by reading the existing console, menu, and Streamlit files instead
  of assuming the app already had working web behavior.
- Clarifying the desired web/console relationship led to a shared-order design:
  Supabase for hosted persistence, with the local API retained for development.
- We caught an important deployment mismatch: Streamlit Cloud was running
  `main.py`, the console entry point, instead of `streamlit_app.py`.
- The menu was kept in text files as requested. Prices were added to unpriced
  items only after the owner supplied the price rules.
- The app now uses Streamlit Session State for the in-progress cart and
  Supabase for orders that must survive after the browser session.
- We tested menu validation, API behavior, Supabase client requests, cart
  behavior, Central Time conversion, and the itemized order summary.
- The owner successfully deployed the app and kept the Supabase secret in a
  password manager rather than sharing it.

## What could have been better

- I should have identified the Streamlit Cloud/localhost boundary earlier.
  A Cloud app cannot reach an API at `127.0.0.1` on the owner's computer.
- I should have checked the deployed entry-point setting sooner. Several
  troubleshooting steps could have been avoided by confirming that Cloud was
  running `streamlit_app.py`, not `main.py`.
- I should have distinguished the Supabase GitHub branching integration from
  normal migrations earlier, and verified the free-plan workflow before
  suggesting branch-related steps.
- I made avoidable generated-file and line-ending noise while checking time
  handling. Future edits should stay focused on active code paths and inspect
  the diff before considering a change complete.
- When reviewing screenshots, I should state exactly which portion is visible
  and avoid implying that a detail is confirmed if the image is too small or
  cropped.

## What the owner could have done better

- When reporting a deployment problem, include the exact visible error text or
  a readable screenshot, and mention whether the app was just redeployed.
- For deployment questions, sharing the selected repository, branch, and main
  file path together makes it easier to isolate configuration issues.
- Continue keeping credentials in the password manager and never paste secret
  keys into chat or commit them to GitHub.

## What we learned

- Streamlit Community Cloud runs the configured entry-point file. For this
  project it must be `streamlit_app.py`; `main.py` is the console client.
- The local API is for local development. Hosted orders require an internet-
  reachable backend, which this project implements with Supabase.
- Session State is suitable for the current browser session's cart; Supabase
  is the durable store for completed orders shared with the console.
- Supabase timestamps represent instants and may be returned in UTC. The app
  creates timezone-aware Central Time timestamps and converts saved timestamps
  to `America/Chicago` for console display, observing CST/CDT.
- Usability details matter: show unit prices and extended line prices beside
  selected items, while retaining subtotal and tax-inclusive total.
- Automated tests and a real browser check each catch different issues; both
  were useful in this work.
