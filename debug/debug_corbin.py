def debug_corbin():
    print(f"\n{CYAN}{BOLD}━━━ Corbin (direct) ━━━{RESET}")

    with open("corbin_bank_accounts.csv") as f:
        accounts = list(csv.DictReader(f))
    acc = next(a for a in accounts if a["AccountStatus"] == "Active")

    print(f"  Account: {acc}")  # print full account row

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
        "username":     "orodriguez",  # updated credentials
        "password":     r"91/l%\[]8bSS[i7G",
    }
    r = requests.post(
        "hhttps://xbu6ixwga4.execute-api.us-west-2.amazonaws.com/default/handleTransaction",  # updated URL
        json=payload, headers=headers
    )
    print(f"  HTTP status: {r.status_code}")
    print(f"  Raw response: {r.text}")