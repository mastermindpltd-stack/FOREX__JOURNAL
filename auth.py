import streamlit_authenticator as stauth

def get_authenticator():

    credentials = {
        "usernames": {
            "vicky": {
                "name": "Vicky",
                "password": stauth.Hasher(["12345"]).generate()[0]
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
