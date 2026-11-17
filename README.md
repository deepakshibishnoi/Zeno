# Zeno Haircare Chatbot — Streamlit

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your Gemini API key as an environment variable:

   **macOS / Linux**
   ```bash
   export GEMINI_API_KEY="YOUR_NEW_GEMINI_API_KEY"
   ```

   **Windows PowerShell**
   ```powershell
   $env:GEMINI_API_KEY="YOUR_NEW_GEMINI_API_KEY"
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Upload these project files to a GitHub repository.
2. In Streamlit Community Cloud, create a new app and select `app.py`.
3. Open the app's **Settings → Secrets** and add:

   ```toml
   GEMINI_API_KEY = "YOUR_NEW_GEMINI_API_KEY"
   ```

4. Save and redeploy.

## Important API-key security

The source text you supplied contained an API key in plain text. Treat that key as exposed:
revoke/delete it in Google AI Studio and create a new key. Do not put the new key in `app.py`
or commit it to GitHub. Use Streamlit Secrets or the environment variable as described above.

## Notes

- The original script described automatic location, currency, weather, live product verification,
  and price crawling, but did not implement those integrations. This Streamlit conversion does
  not pretend those features are active.
- Product prices, availability, and ingredient lists are not fetched live by this version.
- Photos are optional and are sent to Gemini for visual context when attached.
- Zeno provides general haircare information and is not a substitute for a dermatologist.
