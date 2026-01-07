import streamlit_authenticator as stauth

def get_authenticator():
    credentials = {
        "usernames": {
            "vicky": {
                "name": "Vicky",
                "password": "$2b$12$PASTE_YOUR_HASH_HERE"
            }
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "clean_journal_cookie",
        "clean_journal_key",
        cookie_expiry_days=30
    )

    return authenticator
