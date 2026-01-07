import streamlit_authenticator as stauth

# -------------------------------------------------
# USERS (ADD MORE LATER)
# -------------------------------------------------
names = ["Vicky"]
usernames = ["vicky"]

# IMPORTANT:
# Passwords must be hashed ONCE
# Use: stauth.Hasher(["password"]).generate()
hashed_passwords = [
    "$2b$12$0q1Yz8y2Xx9oK9ZcXj6P7O5uQ1nX5cP8sX6Wj5b1H2s0m1GQ3Y6nW"
]
# above hash is for password: 12345

# -------------------------------------------------
# AUTHENTICATOR
# -------------------------------------------------
def get_authenticator():
    authenticator = stauth.Authenticate(
        {
            "usernames": {
                "vicky": {
                    "name": "Vicky",
                    "password": hashed_passwords[0]
                }
            }
        },
        "clean_journal_cookie",   # cookie name
        "clean_journal_key",      # signature key
        cookie_expiry_days=30
    )
    return authenticator
