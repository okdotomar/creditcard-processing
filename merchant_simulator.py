import requests
import random
import datetime
import json

# ── YOUR API URL ─────────────────────────────────────────────────────────────
URL = "https://v3k5iwm6zf.execute-api.us-west-2.amazonaws.com/default/processCard"
LOG_FILE = "transaction_log.txt"

# ── BANK ACCOUNTS FROM CSV ───────────────────────────────────────────────────
accounts = [
    {"card_holder": "Ava Jensen",       "card_num": "4539148803436467", "exp_date": "09/28", "cvv": "184", "card_zip": "84770", "balance": 1250.75, "credit_limit": 3000.00,  "credit_used": 420.15},
    {"card_holder": "Noah Ramirez",     "card_num": "4716461583322103", "exp_date": "12/27", "cvv": "907", "card_zip": "84790", "balance": 82.19,   "credit_limit": 1500.00,  "credit_used": 1499.99},
    {"card_holder": "Mia Thompson",     "card_num": "4485921786505210", "exp_date": "03/29", "cvv": "512", "card_zip": "84101", "balance": 5600.00,  "credit_limit": 10000.00, "credit_used": 0.00},
    {"card_holder": "Ethan Lee",        "card_num": "4556737586899855", "exp_date": "07/26", "cvv": "033", "card_zip": "84015", "balance": 14.02,   "credit_limit": 500.00,   "credit_used": 212.48},
    {"card_holder": "Sophia Patel",     "card_num": "4916650436143859", "exp_date": "11/30", "cvv": "771", "card_zip": "84660", "balance": 230.10,  "credit_limit": 2500.00,  "credit_used": 2500.00},
    {"card_holder": "Liam Carter",      "card_num": "4532756279624064", "exp_date": "04/28", "cvv": "648", "card_zip": "84770", "balance": 980.33,  "credit_limit": 2000.00,  "credit_used": 150.00},
    {"card_holder": "Olivia Nguyen",    "card_num": "4024007175860431", "exp_date": "10/27", "cvv": "291", "card_zip": "84790", "balance": 0.00,    "credit_limit": 1200.00,  "credit_used": 1199.50},
    {"card_holder": "Jackson Wright",   "card_num": "4539976741512043", "exp_date": "01/27", "cvv": "406", "card_zip": "84321", "balance": 310.45,  "credit_limit": 800.00,   "credit_used": 799.99},
    {"card_holder": "Isabella Martinez","card_num": "4556318984301377", "exp_date": "06/29", "cvv": "118", "card_zip": "84097", "balance": 7420.12, "credit_limit": 15000.00, "credit_used": 3200.00},
    {"card_holder": "Lucas Brown",      "card_num": "4716108999710720", "exp_date": "08/26", "cvv": "954", "card_zip": "84770", "balance": 65.00,   "credit_limit": 1000.00,  "credit_used": 0.00},
    {"card_holder": "Amelia Scott",     "card_num": "4485487807732470", "exp_date": "05/28", "cvv": "602", "card_zip": "84604", "balance": 199.99,  "credit_limit": 3000.00,  "credit_used": 2750.25},
    {"card_holder": "Benjamin Hill",    "card_num": "4532115610653722", "exp_date": "02/27", "cvv": "225", "card_zip": "84003", "balance": 120.00,  "credit_limit": 600.00,   "credit_used": 599.00},
]

# ── VALID MERCHANTS ──────────────────────────────────────────────────────────
merchants = [
    {"name": "Bear Paw Cafe",    "token": "0PDOt87g"},
    {"name": "Costco",           "token": "DZXBV92s"},
    {"name": "Walmart",          "token": "260fZojB"},
    {"name": "Smiths",           "token": "TlAnbSU1"},
    {"name": "Costa Vida",       "token": "AzFM4BXv"},
    {"name": "Arctic Circle",    "token": "OCmngQJ4"},
]

# ── HELPERS ──────────────────────────────────────────────────────────────────
def timestamp():
    return str(datetime.datetime.now())

def small_amount():
    return str(round(random.uniform(1.00, 9.99), 2))

def make_request(payload):
    try:
        result = requests.post(URL, json=payload, timeout=20)
        return result.text.strip()
    except Exception as e:
        return f"Request failed: {str(e)}"

def log(f, payload, response):
    merchant = payload.get("merchant_name", "unknown")
    token    = payload.get("merchant_token", "unknown")
    holder   = payload.get("customer_name", "unknown")
    bank     = payload.get("bank", "unknown")
    txn_type = payload.get("card_type", "unknown")
    zip_code = payload.get("card_zip", "unknown")
    amount   = payload.get("amount", "unknown")
    ts       = payload.get("timestamp", "unknown")

    f.write("-" * 50 + "\n")
    f.write(f"Merchant Request: {merchant},{token},{holder},{bank},{txn_type},{zip_code},${amount},{ts}\n")
    f.write(f"Response: {response}\n")
    f.write("-" * 50 + "\n\n")
    print(f"[{response}] {merchant} | {holder} | ${amount}")

# ── BUILD TEST CASES ─────────────────────────────────────────────────────────
# ── BUILD TEST CASES ─────────────────────────────────────────────────────────
def build_tests():
    tests = []
    m = merchants

    # 1. Good debit transactions - various merchants and cardholders (10 tests)
    good_debit_accounts = ["Mia Thompson", "Isabella Martinez", "Liam Carter", "Ava Jensen", "Benjamin Hill"]
    for name in good_debit_accounts:
        acct = next(a for a in accounts if a["card_holder"] == name)
        merch = random.choice(m)
        tests.append(("good_debit", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))
        # run each twice with different merchants
        merch2 = random.choice(m)
        tests.append(("good_debit", {
            "bank": "Jeffs Bank",
            "merchant_name": merch2["name"],
            "merchant_token": merch2["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 2. Good credit transactions (5 tests)
    good_credit_accounts = ["Liam Carter", "Mia Thompson", "Isabella Martinez"]
    for name in good_credit_accounts:
        acct = next(a for a in accounts if a["card_holder"] == name)
        merch = random.choice(m)
        tests.append(("good_credit", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "credit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 3. Bad merchant token (5 tests)
    for _ in range(5):
        acct = random.choice(accounts)
        merch = random.choice(m)
        tests.append(("bad_merchant_token", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": "BADTOKEN1",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 4. Insufficient funds (5 tests)
    low_balance = ["Noah Ramirez", "Ethan Lee", "Olivia Nguyen", "Lucas Brown"]
    for name in low_balance:
        acct = next(a for a in accounts if a["card_holder"] == name)
        merch = random.choice(m)
        tests.append(("insufficient_funds", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": "500.00",
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 5. Bad CVV (3 tests)
    for _ in range(3):
        acct = random.choice(accounts)
        merch = random.choice(m)
        tests.append(("bad_cvv", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": "000",
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 6. Bad expiration date (3 tests)
    for _ in range(3):
        acct = random.choice(accounts)
        merch = random.choice(m)
        tests.append(("bad_exp_date", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": "01/20",
            "timestamp": timestamp()
        }))

    # 7. Bad zip code (3 tests)
    for _ in range(3):
        acct = random.choice(accounts)
        merch = random.choice(m)
        tests.append(("bad_zip", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": "00000",
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 8. Bad account number (3 tests)
    for _ in range(3):
        merch = random.choice(m)
        tests.append(("bad_account_number", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "0000000000000000",
            "customer_name": "Fake Person",
            "cc_num": "0000000000000000",
            "card_type": "debit",
            "cvv": "000",
            "amount": small_amount(),
            "card_zip": "00000",
            "exp_date": "01/20",
            "timestamp": timestamp()
        }))

    # 9. Unsupported bank (3 tests)
    for _ in range(3):
        acct = random.choice(accounts)
        merch = random.choice(m)
        tests.append(("unsupported_bank", {
            "bank": "Fake Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Fake Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 10. Extra valid transactions to reach 50+ total (8 more)
    extra = ["Ava Jensen", "Isabella Martinez", "Mia Thompson", "Liam Carter",
             "Benjamin Hill", "Ava Jensen", "Isabella Martinez", "Mia Thompson"]
    for name in extra:
        acct = next(a for a in accounts if a["card_holder"] == name)
        merch = random.choice(m)
        tests.append(("good_debit_extra", {
            "bank": "Jeffs Bank",
            "merchant_name": merch["name"],
            "merchant_token": merch["token"],
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": acct["card_num"],
            "customer_name": acct["card_holder"],
            "cc_num": acct["card_num"],
            "card_type": "debit",
            "cvv": acct["cvv"],
            "amount": small_amount(),
            "card_zip": acct["card_zip"],
            "exp_date": acct["exp_date"],
            "timestamp": timestamp()
        }))

    # 11. Malformed / missing fields (5 tests)
    tests.append(("missing_cc_num", {
        "bank": "Jeffs Bank",
        "merchant_name": "Bear Paw Cafe",
        "merchant_token": "0PDOt87g",
        "customer_name": "Benjamin Hill",
        "card_type": "debit",
        "cvv": "225",
        "amount": "5.00",
        "card_zip": "84003",
        "exp_date": "02/27",
        "timestamp": timestamp()
    }))
    tests.append(("missing_amount", {
        "bank": "Jeffs Bank",
        "merchant_name": "Bear Paw Cafe",
        "merchant_token": "0PDOt87g",
        "merchant_bank_acct": "4532115610653722",
        "customer_name": "Benjamin Hill",
        "cc_num": "4532115610653722",
        "card_type": "debit",
        "cvv": "225",
        "card_zip": "84003",
        "exp_date": "02/27",
        "timestamp": timestamp()
    }))
    tests.append(("missing_customer_name", {
        "bank": "Jeffs Bank",
        "merchant_name": "Bear Paw Cafe",
        "merchant_token": "0PDOt87g",
        "merchant_bank_acct": "4532115610653722",
        "cc_num": "4532115610653722",
        "card_type": "debit",
        "cvv": "225",
        "amount": "5.00",
        "card_zip": "84003",
        "exp_date": "02/27",
        "timestamp": timestamp()
    }))
    tests.append(("missing_bank", {
        "merchant_name": "Bear Paw Cafe",
        "merchant_token": "0PDOt87g",
        "merchant_bank_acct": "4532115610653722",
        "customer_name": "Benjamin Hill",
        "cc_num": "4532115610653722",
        "card_type": "debit",
        "cvv": "225",
        "amount": "5.00",
        "card_zip": "84003",
        "exp_date": "02/27",
        "timestamp": timestamp()
    }))
    tests.append(("empty_payload", {}))

    return tests

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    tests = build_tests()
    print(f"Running {len(tests)} test transactions...\n")

    with open(LOG_FILE, "w") as f:
        f.write("=" * 50 + "\n")
        f.write(f"TRANSACTION LOG - {timestamp()}\n")
        f.write(f"Total transactions: {len(tests)}\n")
        f.write("=" * 50 + "\n\n")

        for i, (test_type, payload) in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] {test_type}")
            response = make_request(payload)
            f.write(f"Test Type: {test_type}\n")
            log(f, payload, response)

        f.write("=" * 50 + "\n")
        f.write(f"SIMULATION COMPLETE - {timestamp()}\n")
        f.write("=" * 50 + "\n")

    print(f"\nDone! Log written to {LOG_FILE}")
    print(f"Total transactions: {len(tests)}")

if __name__ == "__main__":
    main()