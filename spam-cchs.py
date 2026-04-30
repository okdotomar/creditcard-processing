import csv
import glob
import json
import os
import random
import time
from datetime import datetime, timezone

import requests


MERCHANT_FILE = "merchants.csv"
URLS_FILE = "urls.txt"
LOG_FILE = "bank_endpoint_log.txt"

REQUEST_TIMEOUT = 12
SLEEP_BETWEEN_CALLS = 1
SLEEP_BETWEEN_PASSES = 2

BANK_FILE_TO_NAME = {
    "jeffs_bank_accounts.csv": "Jeffs Bank",
    "tophers_bank_accounts.csv": "Tophers Bank",
    "jankbank_bank_accounts.csv": "JankBank",
    "calibear_bank_accounts.csv": "CaliBear",
    "wildwestbank_bank_accounts.csv": "Wild West Bank",
    "corbin_bank_accounts.csv": "Corbin",
}


def read_csv_rows(filename):
    with open(filename, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_merchants(filename=MERCHANT_FILE):
    merchants = []
    rows = read_csv_rows(filename)

    for row in rows:
        name = (row.get("Name") or "").strip()
        token = (row.get("Token") or "").strip()

        if name and token:
            merchants.append({
                "merchant_name": name,
                "merchant_token": token,
            })

    return merchants


def load_endpoints(filename=URLS_FILE):
    endpoints = []

    with open(filename, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            url = (row.get("url") or "").strip()

            if name and url:
                endpoints.append((name, url))

    return endpoints


def plausible_cvv():
    return f"{random.randint(100, 999)}"


def plausible_zip():
    return f"{random.randint(10000, 99999)}"


def plausible_exp_date():
    month = random.randint(1, 12)
    year = random.randint(27, 31)
    return f"{month:02d}/{year}"


def random_amount():
    return f"{random.uniform(1.00, 19.99):.2f}"


def get_first_present(row, keys, default=""):
    for key in keys:
        value = row.get(key)
        if value is not None:
            value = str(value).strip()
            if value != "":
                return value
    return default


def infer_card_type(row):
    # Prefer explicit type if present
    explicit = get_first_present(
        row,
        ["CardType", "card_type", "AccountType", "account_type", "Type", "type"]
    ).lower()

    if explicit in ("credit", "debit"):
        return explicit

    # Infer from credit-related columns if present
    credit_limit = get_first_present(
        row,
        ["credit_limit", "CreditLimit", "creditLimit", "Credit Limit"]
    )

    if credit_limit not in ("", "0", "0.0", "0.00"):
        return random.choice(["credit", "debit"])

    # Default when unknown
    return random.choice(["credit", "debit"])


def parse_account_row(bank_name, row):
    # Generic mapping approach:
    # take whatever exists, minimal bank-specific column-name recognition only

    first_name = get_first_present(row, ["AccountHolderFirstName", "first_name", "FirstName"])
    last_name = get_first_present(row, ["AccountHolderLastName", "last_name", "LastName"])

    card_holder = get_first_present(
        row,
        [
            "card_holder",
            "AccountHolderName",
            "AccountOwner",
            "Name",
            "account_holder_name",
            "name",
            "FullName",
            "full_name",
        ],
    )

    if not card_holder and (first_name or last_name):
        card_holder = f"{first_name} {last_name}".strip()

    cc_number = get_first_present(
        row,
        [
            "card_num",
            "CardNumber",
            "Card Number",
            "AccountNumber",
            "BankAccountNumber",
            "cc_number",
            "account_number",
            "number",
        ],
    )

    cvv = get_first_present(row, ["cvv", "CVV"])
    exp_date = get_first_present(
        row,
        ["exp_date", "ExpDate", "ExpirationDate", "Card Expiration Date", "expiration_date"]
    )
    card_zip = get_first_present(row, ["card_zip", "ZipCode", "ZIP Code", "zip", "zip_code"])
    card_type = infer_card_type(row)

    if not cvv:
        cvv = plausible_cvv()

    if not exp_date:
        exp_date = plausible_exp_date()

    if not card_zip:
        card_zip = plausible_zip()

    if not card_holder or not cc_number:
        return None

    return {
        "bank": bank_name,
        "card_holder": card_holder,
        "cc_number": cc_number,
        "card_type": card_type,
        "cvv": cvv,
        "exp_date": exp_date,
        "card_zip": card_zip,
    }


def load_bank_accounts():
    bank_accounts = {}
    total_loaded = 0
    total_skipped = 0

    for filename in glob.glob("*_bank_accounts.csv"):
        basename = os.path.basename(filename)
        bank_name = BANK_FILE_TO_NAME.get(basename)

        if not bank_name:
            continue

        rows = read_csv_rows(filename)
        bank_accounts[bank_name] = []

        for row in rows:
            account = parse_account_row(bank_name, row)
            if account is None:
                total_skipped += 1
                continue

            bank_accounts[bank_name].append(account)
            total_loaded += 1

    print(f"Loaded {total_loaded} bank accounts")
    print(f"Skipped {total_skipped} unusable rows")

    return bank_accounts


def make_timestamp():
    return datetime.now(timezone.utc).isoformat()


def make_transaction(merchants, bank_accounts):
    merchant = random.choice(merchants)

    available_banks = [bank for bank, accounts in bank_accounts.items() if accounts]
    if not available_banks:
        raise RuntimeError("No banks with usable accounts were loaded")

    bank_name = random.choice(available_banks)
    account = random.choice(bank_accounts[bank_name])

    return {
        "bank": bank_name,
        "merchant_name": merchant["merchant_name"],
        "merchant_token": merchant["merchant_token"],
        "card_holder": account["card_holder"],
        "cc_number": account["cc_number"],
        "card_type": account["card_type"],
        "cvv": account["cvv"],
        "exp_date": account["exp_date"],
        "amount": random_amount(),
        "card_zip": account["card_zip"],
        "timestamp": make_timestamp(),
    }


def extract_message(response):
    try:
        data = response.json()

        if isinstance(data, dict):
            if "message" in data:
                return str(data["message"])

            if "body" in data:
                body_value = data["body"]
                if isinstance(body_value, str):
                    try:
                        parsed_body = json.loads(body_value)
                        if isinstance(parsed_body, dict) and "message" in parsed_body:
                            return str(parsed_body["message"])
                        return json.dumps(parsed_body)
                    except Exception:
                        return str(body_value)

            return json.dumps(data)

        return str(data)

    except Exception:
        return response.text.strip()


def print_result(student_name, payload, status_code, message):
    print("=============")
    print(f'calling "{student_name}" :')
    print(f'merchant: {payload["merchant_name"]}')
    print(f'card_holder: {payload["card_holder"]}')
    print(f'bank: {payload["bank"]}')
    print(f'amount: {payload["amount"]}')
    print(f'credit/debit: {payload["card_type"]}')
    print(f"Results: {status_code} {message}")
    print("==============")
    print()


def append_log(student_name, url, payload, status_code, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("=============\n")
        f.write(f"time: {datetime.now().isoformat()}\n")
        f.write(f'calling "{student_name}" :\n')
        f.write(f"url: {url}\n")
        f.write(f'merchant: {payload["merchant_name"]}\n')
        f.write(f'card_holder: {payload["card_holder"]}\n')
        f.write(f'bank: {payload["bank"]}\n')
        f.write(f'amount: {payload["amount"]}\n')
        f.write(f'credit/debit: {payload["card_type"]}\n')
        f.write(f'payload: {json.dumps(payload)}\n')
        f.write(f"Results: {status_code} {message}\n")
        f.write("==============\n\n")


def main():
    merchants = load_merchants(MERCHANT_FILE)
    endpoints = load_endpoints(URLS_FILE)
    bank_accounts = load_bank_accounts()

    if not merchants:
        raise RuntimeError("No merchants loaded from merchants.csv")

    if not endpoints:
        raise RuntimeError("No endpoints loaded from urls.txt")

    if not any(bank_accounts.values()):
        raise RuntimeError("No usable bank accounts loaded")

    print(f"Loaded {len(merchants)} merchants")
    print(f"Loaded {len(endpoints)} endpoints")
    print(f"Loaded banks: {', '.join(sorted([b for b, a in bank_accounts.items() if a]))}")
    print(f"Logging to {LOG_FILE}")
    print()

    while True:
        for student_name, url in endpoints:
            payload = make_transaction(merchants, bank_accounts)

            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=REQUEST_TIMEOUT,
                )
                message = extract_message(response)
                print_result(student_name, payload, response.status_code, message)
                append_log(student_name, url, payload, response.status_code, message)

            except requests.exceptions.Timeout:
                message = "Request timed out"
                print_result(student_name, payload, "TIMEOUT", message)
                append_log(student_name, url, payload, "TIMEOUT", message)

            except Exception as e:
                message = f"ERROR: {e}"
                print_result(student_name, payload, "ERROR", message)
                append_log(student_name, url, payload, "ERROR", message)

            time.sleep(SLEEP_BETWEEN_CALLS)

        time.sleep(SLEEP_BETWEEN_PASSES)


if __name__ == "__main__":
    main()
