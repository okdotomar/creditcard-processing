"""
debug_banks.py
Calls each bank DIRECTLY (bypasses your Lambda) to see raw responses.
This helps diagnose credential and field mapping issues.
Run: python3 debug_banks.py
"""

import requests
import json
import csv

CYAN  = "\033[96m"
BOLD  = "\033[1m"
RESET = "\033[0m"
RED   = "\033[91m"
GREEN = "\033[92m"

def show(bank, payload, response, headers_sent=None):
    print(f"\n  Sent payload:  {json.dumps(payload, indent=4)}")
    if headers_sent:
        print(f"  Sent headers:  {headers_sent}")
    print(f"  HTTP status:   {response.status_code}")
    print(f"  Raw response:  {response.text[:300]}")

# ── CaliBear ──────────────────────────────────────────────────────────────────
def debug_calibear():
    print(f"\n{CYAN}{BOLD}━━━ CaliBear (direct) ━━━{RESET}")

    with open("barrett_bank_accounts-1.csv") as f:
        acc = list(csv.DictReader(f))[0]  # first account

    payload = {
        "clearinghouse_id": "rodriguez_o_cch",
        "card_number":      acc["CardNumber"],
        "amount":           50.00,
        "transaction_type": "withdrawal",
        "merchant_name":    "Contact Climbing",
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key":    "credential_token_qbkk4cij2v2heifjfc2v37p",
    }
    r = requests.post("https://api.calibear.credit/transaction/", json=payload, headers=headers)
    show("CaliBear", payload, r, {"x-api-key": "credential_token_qbkk4cij2v2heifjfc2v37p"})

# ── Corbin ────────────────────────────────────────────────────────────────────
def debug_corbin():
    print(f"\n{CYAN}{BOLD}━━━ Corbin (direct) ━━━{RESET}")

    with open("corbin_bank_accounts.csv") as f:
        accounts = list(csv.DictReader(f))
    acc = next(a for a in accounts if a["AccountStatus"] == "Active")

    payload = {
        "account_num":      acc["BankAccountNumber"],
        "cvv":              acc["CVV"],
        "exp_date":         acc["ExpDate"],
        "amount":           "50.00",
        "transaction_type": "withdrawal",
        "card_type":        acc["CardType"],
    }
    headers = {
        "Content-Type": "application/json",
        "username":     "rodriguez_cch",
        "password":     "x2T9vB5W",
    }
    r = requests.post(
        "https://xbu6ixwga4.execute-api.us-west-2.amazonaws.com/default/handleTransaction",
        json=payload, headers=headers
    )
    show("Corbin", payload, r, {"username": "rodriguez_cch", "password": "x2T9vB5W"})

# ── Josephs Bank ──────────────────────────────────────────────────────────────
def debug_josephs():
    print(f"\n{CYAN}{BOLD}━━━ Josephs Bank (direct) ━━━{RESET}")

    with open("joseph_bank_accounts-1.csv") as f:
        acc = list(csv.DictReader(f))[0]

    payload = {
        "cch_name":    "orodriguez",
        "cch_token":   "Ao3iHhMIJzL6VxPALFJ1W7rb4Ma06oRi",
        "account_num": acc["Account Number"],
        "card_num":    acc["Card Number"],
        "exp_date":    acc["Card Expiration Date"],
        "cvv":         acc["CVV"],
        "amount":      "50.00",
        "type":        "debit",
        "merchant":    "Contact Climbing",
    }
    r = requests.post(
        "https://yt1i4wstmb.execute-api.us-west-2.amazonaws.com/default/transact",
        json=payload
    )
    show("Josephs", payload, r)

# ── Wild West ─────────────────────────────────────────────────────────────────
def debug_wild_west():
    print(f"\n{CYAN}{BOLD}━━━ Wild West (direct) ━━━{RESET}")

    with open("deanna_bank_accounts-1.csv") as f:
        acc = list(csv.DictReader(f))[0]

    payload = {
        "cch_name":            "rodriguez_cch",
        "cch_token":           "x2T9vB5W",
        "account_holder_name": acc["AccountHolderName"],
        "account_number":      acc["AccountNumber"],
        "transaction_type":    "withdrawal",
        "card_type":           "debit",
        "amount":              "50.00",
    }
    r = requests.post(
        "https://l25ft7pzu5wpwm3xtskoiks6rm0javto.lambda-url.us-west-2.on.aws/",
        json=payload
    )
    show("Wild West", payload, r)

# ── Tophers credit ────────────────────────────────────────────────────────────
def debug_tophers_credit():
    print(f"\n{CYAN}{BOLD}━━━ Tophers Credit (direct) ━━━{RESET}")

    with open("topher_accounts_table-1.csv") as f:
        accounts = list(csv.DictReader(f))
    active = [a for a in accounts if a["AccountStatus"] == "ACTIVE"]
    acc = active[3]  # first credit test account

    payload = {
        "cch_name":         "orodriguez_cch",
        "cch_token":        "E4uW5cJh",
        "card_number":      acc["CardNumber"],
        "cvv":              acc["CVVHash"],
        "exp_date":         acc["ExpirationDate"],
        "amount":           50.00,
        "transaction_type": "credit",
        "merchant_name":    "Contact Climbing",
        "withdrawal":       False,
    }
    r = requests.post(
        "https://lp4uqktsqg.execute-api.us-west-2.amazonaws.com/default/doRequest",
        json=payload
    )
    show("Tophers Credit", payload, r)


if __name__ == "__main__":
    print(f"\n{BOLD}{'━'*60}")
    print(f"  Direct Bank Debug — Raw Responses")
    print(f"{'━'*60}{RESET}")

    debug_calibear()
    debug_corbin()
    debug_josephs()
    debug_wild_west()
    debug_tophers_credit()