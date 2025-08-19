import os


def get_contact():
    return {
        "email": "chaudreyadnan@gmail.com",
        "phone": "",
        "wallet": os.getenv("USER_WALLET_ADDRESS", "")
    }


def get_terms():
    return {"text": open("docs/terms.md").read() if os.path.exists("docs/terms.md") else "Terms coming soon."}


def get_privacy():
    return {"text": open("docs/privacy.md").read() if os.path.exists("docs/privacy.md") else "Privacy policy coming soon."}

