import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()


class Secrets(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


secrets = Secrets(
    {
        "ZOHO_ACCOUNTS_HOST": os.getenv("ZOHO_ACCOUNTS_HOST"),
        "ZOHO_MAIL_HOST": os.getenv("ZOHO_MAIL_HOST"),
        "ZOHO_CLIENT_ID": os.getenv("ZOHO_CLIENT_ID"),
        "ZOHO_CLIENT_SECRET": os.getenv("ZOHO_CLIENT_SECRET"),
        "ZOHO_REFRESH_TOKEN": os.getenv("ZOHO_REFRESH_TOKEN"),
        "ZOHO_ACCOUNT_ID": os.getenv("ZOHO_ACCOUNT_ID"),
        "from_addr": os.getenv("ZOHO_FROM_ADDR"),
        "to_addr": os.getenv("ZOHO_TO_ADDR"),
        "subject": os.getenv("ZOHO_SUBJECT"),
    }
)

for key, value in secrets.items():
    if value is None:
        raise ValueError(f"Environment variable {key} is not set.")


def get_access_token(accounts_host, client_id, client_secret, refresh_token):
    url = f"https://{accounts_host}/oauth/v2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    # print(r.json()["access_token"])
    return r.json()["access_token"]


def list_accounts(mail_host):

    access_token = get_access_token(
        accounts_host=secrets.ZOHO_ACCOUNTS_HOST,
        client_id=secrets.ZOHO_CLIENT_ID,
        client_secret=secrets.ZOHO_CLIENT_SECRET,
        refresh_token=secrets.ZOHO_REFRESH_TOKEN,
    )

    url = f"https://{mail_host}/api/accounts"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Accept": "application/json",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))
    return r.json()


def send_mail(html):

    from_addr = secrets.from_addr
    to_addr = secrets.to_addr
    subject = secrets.subject
    mail_host = secrets.ZOHO_MAIL_HOST
    account_id = secrets.ZOHO_ACCOUNT_ID

    access_token = get_access_token(
        accounts_host=secrets.ZOHO_ACCOUNTS_HOST,
        client_id=secrets.ZOHO_CLIENT_ID,
        client_secret=secrets.ZOHO_CLIENT_SECRET,
        refresh_token=secrets.ZOHO_REFRESH_TOKEN,
    )

    url = f"https://{mail_host}/api/accounts/{account_id}/messages"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    body = {
        "fromAddress": from_addr,
        "toAddress": to_addr,
        "subject": subject,
        "content": html,
        "mailFormat": "html",
    }

    try:
        print(f"\tSending notification email to {to_addr}...")
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending email: {e}")

    return r.json()
