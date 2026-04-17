"""
testBanks.py
Reads all bank CSV account files and tests your clearinghouse API.
Usage: python3 testBanks.py

PASS = any valid bank response (Approved OR a meaningful Decline)
FAIL = system errors (Server Error, Merchant Not Authorized, Bank Not Supported, exceptions)
"""

import requests
import csv
import time
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
CCH_URL        = "https://v3k5iwm6zf.execute-api.us-west-2.amazonaws.com/default/processCard"
MERCHANT_NAME  = "Contact Climbing"
MERCHANT_TOKEN = "ciAnLzvE"
TIMESTAMP      = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
AMOUNT         = "50.00"
DELAY          = 0.4

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

results = []

# ── What counts as a PASS ─────────────────────────────────────────────────────
SYSTEM_ERRORS = [
    "server error",
    "merchant not authorized",
    "bank not supported",
    "invalid request",
    "request failed",
]

def is_pass(message):
    """
    PASS = bank responded with anything meaningful (approved or a real decline).
    FAIL = our system failed to reach the bank or had an internal error.
    """
    msg = message.lower()
    return not any(e in msg for e in SYSTEM_ERRORS)

def status_label(message, expected_decline=False):
    """Return colored label based on response."""
    msg = message.lower()
    if "approved" in msg:
        return f"{GREEN}{BOLD}[APPROVED]{RESET}"
    if expected_decline and is_pass(message):
        return f"{YELLOW}{BOLD}[DECLINED ✓]{RESET}"  # expected decline, working correctly
    if is_pass(message):
        return f"{YELLOW}{BOLD}[DECLINED]{RESET}"
    return f"{RED}{BOLD}[FAIL]{RESET}"


def send(payload, label, expected_decline=False):
    try:
        resp    = requests.post(CCH_URL, json=payload, timeout=15)
        message = resp.text.strip()
        passed  = is_pass(message)
        label_str = status_label(message, expected_decline)

        print(f"  {label_str} {label}")
        print(f"         Response: {message}")

        results.append({
            "bank":    payload.get("bank"),
            "label":   label,
            "passed":  passed,
            "message": message,
            "expected_decline": expected_decline,
        })

    except Exception as e:
        print(f"  {RED}{BOLD}[FAIL]{RESET} {label}")
        print(f"         Exception: {str(e)}")
        results.append({
            "bank":    payload.get("bank"),
            "label":   label,
            "passed":  False,
            "message": f"Request failed: {str(e)}",
            "expected_decline": expected_decline,
        })

    time.sleep(DELAY)


def base_payload(bank):
    return {
        "bank":           bank,
        "merchant_name":  MERCHANT_NAME,
        "merchant_token": MERCHANT_TOKEN,
        "timestamp":      TIMESTAMP,
        "amount":         AMOUNT,
    }


# ══════════════════════════════════════════════════════════════════════════════
# JEFFS BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_jeffs_bank():
    print(f"\n{CYAN}{BOLD}━━━ Jeffs Bank ━━━{RESET}")
    with open("jeff-acounts1.csv") as f:
        accounts = list(csv.DictReader(f))

    for acc in accounts[:3]:
        p = base_payload("Jeffs Bank")
        p.update({"cc_number": acc["card_num"], "card_holder": acc["card_holder"],
                   "card_zip": acc["card_zip"], "cvv": acc["cvv"],
                   "exp_date": acc["exp_date"], "card_type": "debit"})
        send(p, f"Debit — {acc['card_holder']} (...{acc['card_num'][-4:]})")

    for acc in accounts[3:6]:
        p = base_payload("Jeffs Bank")
        p.update({"cc_number": acc["card_num"], "card_holder": acc["card_holder"],
                   "card_zip": acc["card_zip"], "cvv": acc["cvv"],
                   "exp_date": acc["exp_date"], "card_type": "credit"})
        send(p, f"Credit — {acc['card_holder']} (...{acc['card_num'][-4:]})")

    acc = accounts[6]
    p = base_payload("Jeffs Bank")
    p.update({"cc_number": acc["card_num"], "card_holder": acc["card_holder"],
               "card_zip": acc["card_zip"], "cvv": acc["cvv"],
               "exp_date": acc["exp_date"], "card_type": "deposit"})
    send(p, f"Deposit — {acc['card_holder']} (...{acc['card_num'][-4:]})")


# ══════════════════════════════════════════════════════════════════════════════
# TOPHERS BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_tophers_bank():
    print(f"\n{CYAN}{BOLD}━━━ Tophers Bank ━━━{RESET}")
    with open("topher_accounts_table-1.csv") as f:
        accounts = list(csv.DictReader(f))

    active     = [a for a in accounts if a["AccountStatus"] == "ACTIVE"]
    delinquent = [a for a in accounts if a["AccountStatus"] == "DELINQUENT"]

    for acc in active[:3]:
        p = base_payload("Tophers Bank")
        p.update({"cc_number": acc["CardNumber"], "card_holder": acc["AccountHolderName"],
                   "card_zip": "84770", "cvv": acc["CVVHash"],
                   "exp_date": acc["ExpirationDate"], "card_type": "debit"})
        send(p, f"Debit — {acc['AccountHolderName']} (...{acc['CardNumber'][-4:]})")

    for acc in active[3:5]:
        p = base_payload("Tophers Bank")
        p.update({"cc_number": acc["CardNumber"], "card_holder": acc["AccountHolderName"],
                   "card_zip": "84770", "cvv": acc["CVVHash"],
                   "exp_date": acc["ExpirationDate"], "card_type": "credit"})
        send(p, f"Credit — {acc['AccountHolderName']} (...{acc['CardNumber'][-4:]})")

    acc = active[5]
    p = base_payload("Tophers Bank")
    p.update({"cc_number": acc["CardNumber"], "card_holder": acc["AccountHolderName"],
               "card_zip": "84770", "cvv": acc["CVVHash"],
               "exp_date": acc["ExpirationDate"], "card_type": "deposit"})
    send(p, f"Deposit — {acc['AccountHolderName']} (...{acc['CardNumber'][-4:]})")

    if delinquent:
        acc = delinquent[0]
        p = base_payload("Tophers Bank")
        p.update({"cc_number": acc["CardNumber"], "card_holder": acc["AccountHolderName"],
                   "card_zip": "84770", "cvv": acc["CVVHash"],
                   "exp_date": acc["ExpirationDate"], "card_type": "debit"})
        send(p, f"Delinquent account — {acc['AccountHolderName']}", expected_decline=True)


# ══════════════════════════════════════════════════════════════════════════════
# WILD WEST BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_wild_west():
    print(f"\n{CYAN}{BOLD}━━━ Wild West Bank ━━━{RESET}")
    with open("deanna_bank_accounts-1.csv") as f:
        accounts = list(csv.DictReader(f))

    for acc in accounts[:3]:
        p = base_payload("Wild West Bank")
        p.update({"cc_number": acc["AccountNumber"], "card_holder": acc["AccountHolderName"],
                   "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "debit"})
        send(p, f"Debit — {acc['AccountHolderName']} (...{acc['AccountNumber'][-4:]})")

    for acc in accounts[3:5]:
        p = base_payload("Wild West Bank")
        p.update({"cc_number": acc["AccountNumber"], "card_holder": acc["AccountHolderName"],
                   "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "credit"})
        send(p, f"Credit — {acc['AccountHolderName']} (...{acc['AccountNumber'][-4:]})")

    acc = accounts[5]
    p = base_payload("Wild West Bank")
    p.update({"cc_number": acc["AccountNumber"], "card_holder": acc["AccountHolderName"],
               "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "deposit"})
    send(p, f"Deposit — {acc['AccountHolderName']} (...{acc['AccountNumber'][-4:]})")


# ══════════════════════════════════════════════════════════════════════════════
# CALIBEAR BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_calibear():
    print(f"\n{CYAN}{BOLD}━━━ CaliBear Bank ━━━{RESET}")
    with open("barrett_bank_accounts-1.csv") as f:
        accounts = list(csv.DictReader(f))

    debit_accounts  = [a for a in accounts if a["AccountType"] == "debit"]
    credit_accounts = [a for a in accounts if a["AccountType"] == "credit"]

    for acc in debit_accounts[:3]:
        name = f"{acc['AccountHolderFirstName']} {acc['AccountHolderLastName']}"
        p = base_payload("Calibear Bank")
        p.update({"cc_number": acc["CardNumber"], "card_holder": name,
                   "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "debit"})
        send(p, f"Debit — {name} (...{acc['CardNumber'][-4:]})")

    for acc in credit_accounts[:2]:
        name = f"{acc['AccountHolderFirstName']} {acc['AccountHolderLastName']}"
        p = base_payload("Calibear Bank")
        p.update({"cc_number": acc["CardNumber"], "card_holder": name,
                   "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "credit"})
        send(p, f"Credit — {name} (...{acc['CardNumber'][-4:]})")

    acc = debit_accounts[3]
    name = f"{acc['AccountHolderFirstName']} {acc['AccountHolderLastName']}"
    p = base_payload("Calibear Bank")
    p.update({"cc_number": acc["CardNumber"], "card_holder": name,
               "card_zip": "84770", "cvv": "000", "exp_date": "12/27", "card_type": "deposit"})
    send(p, f"Deposit — {name} (...{acc['CardNumber'][-4:]})")


# ══════════════════════════════════════════════════════════════════════════════
# CORBIN BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_corbin():
    print(f"\n{CYAN}{BOLD}━━━ Corbin Bank ━━━{RESET}")
    with open("corbin_bank_accounts.csv") as f:
        accounts = list(csv.DictReader(f))

    active   = [a for a in accounts if a["AccountStatus"] == "Active"]
    closed   = [a for a in accounts if a["AccountStatus"] == "Closed"]
    frozen   = [a for a in accounts if a["AccountStatus"] == "Frozen"]
    debit_a  = [a for a in active if a["CardType"] == "debit"]
    credit_a = [a for a in active if a["CardType"] == "credit"]

    for acc in debit_a[:3]:
        p = base_payload("Corbin Bank")
        p.update({"cc_number": acc["BankAccountNumber"], "card_holder": acc["AccountOwner"],
                   "card_zip": acc["ZipCode"], "cvv": acc["CVV"],
                   "exp_date": acc["ExpDate"], "card_type": "debit"})
        send(p, f"Debit — {acc['AccountOwner']} (...{acc['BankAccountNumber'][-4:]})")

    for acc in credit_a[:2]:
        p = base_payload("Corbin Bank")
        p.update({"cc_number": acc["BankAccountNumber"], "card_holder": acc["AccountOwner"],
                   "card_zip": acc["ZipCode"], "cvv": acc["CVV"],
                   "exp_date": acc["ExpDate"], "card_type": "credit"})
        send(p, f"Credit — {acc['AccountOwner']} (...{acc['BankAccountNumber'][-4:]})")

    acc = debit_a[3]
    p = base_payload("Corbin Bank")
    p.update({"cc_number": acc["BankAccountNumber"], "card_holder": acc["AccountOwner"],
               "card_zip": acc["ZipCode"], "cvv": acc["CVV"],
               "exp_date": acc["ExpDate"], "card_type": "deposit"})
    send(p, f"Deposit — {acc['AccountOwner']} (...{acc['BankAccountNumber'][-4:]})")

    if closed:
        acc = closed[0]
        p = base_payload("Corbin Bank")
        p.update({"cc_number": acc["BankAccountNumber"], "card_holder": acc["AccountOwner"],
                   "card_zip": acc["ZipCode"], "cvv": acc["CVV"],
                   "exp_date": acc["ExpDate"], "card_type": acc["CardType"]})
        send(p, f"Closed account — {acc['AccountOwner']}", expected_decline=True)

    if frozen:
        acc = frozen[0]
        p = base_payload("Corbin Bank")
        p.update({"cc_number": acc["BankAccountNumber"], "card_holder": acc["AccountOwner"],
                   "card_zip": acc["ZipCode"], "cvv": acc["CVV"],
                   "exp_date": acc["ExpDate"], "card_type": acc["CardType"]})
        send(p, f"Frozen account — {acc['AccountOwner']}", expected_decline=True)


# ══════════════════════════════════════════════════════════════════════════════
# JOSEPHS BANK
# ══════════════════════════════════════════════════════════════════════════════
def test_josephs_bank():
    print(f"\n{CYAN}{BOLD}━━━ Josephs Bank ━━━{RESET}")
    with open("joseph_bank_accounts-1.csv") as f:
        accounts = list(csv.DictReader(f))

    for acc in accounts[:3]:
        p = base_payload("Josephs Bank")
        p.update({"cc_number": acc["Card Number"], "merchant_bank_acct": acc["Account Number"],
                   "card_holder": acc["Name"], "card_zip": acc["ZIP Code"],
                   "cvv": acc["CVV"], "exp_date": acc["Card Expiration Date"], "card_type": "debit"})
        send(p, f"Debit — {acc['Name']} ({acc['Account Number']})")

    for acc in accounts[3:5]:
        p = base_payload("Josephs Bank")
        p.update({"cc_number": acc["Card Number"], "merchant_bank_acct": acc["Account Number"],
                   "card_holder": acc["Name"], "card_zip": acc["ZIP Code"],
                   "cvv": acc["CVV"], "exp_date": acc["Card Expiration Date"], "card_type": "credit"})
        send(p, f"Credit — {acc['Name']} ({acc['Account Number']})")

    acc = accounts[5]
    p = base_payload("Josephs Bank")
    p.update({"cc_number": acc["Card Number"], "merchant_bank_acct": acc["Account Number"],
               "card_holder": acc["Name"], "card_zip": acc["ZIP Code"],
               "cvv": acc["CVV"], "exp_date": acc["Card Expiration Date"], "card_type": "deposit"})
    send(p, f"Deposit — {acc['Name']} ({acc['Account Number']})")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
def print_summary():
    print(f"\n{BOLD}{'━'*60}{RESET}")
    print(f"{BOLD}  FINAL SUMMARY{RESET}")
    print(f"{BOLD}{'━'*60}{RESET}")

    banks = {}
    for r in results:
        bank = r["bank"]
        if bank not in banks:
            banks[bank] = {"pass": 0, "fail": 0, "failures": []}
        if r["passed"]:
            banks[bank]["pass"] += 1
        else:
            banks[bank]["fail"] += 1
            banks[bank]["failures"].append(r)

    total_pass = sum(b["pass"] for b in banks.values())
    total_fail = sum(b["fail"] for b in banks.values())
    total      = total_pass + total_fail

    for bank, data in banks.items():
        color = GREEN if data["fail"] == 0 else (YELLOW if data["pass"] > 0 else RED)
        print(f"\n  {color}{BOLD}{bank}{RESET}")
        print(f"    Passed: {data['pass']}  |  Failed: {data['fail']}")
        if data["failures"]:
            print(f"    {RED}Failures:{RESET}")
            for f in data["failures"]:
                print(f"      • {f['label']}")
                print(f"        Reason: {f['message']}")

    print(f"\n{BOLD}{'━'*60}{RESET}")
    overall_color = GREEN if total_fail == 0 else (YELLOW if total_pass > 0 else RED)
    print(f"  {overall_color}{BOLD}Total: {total_pass}/{total} passed{RESET}")
    print(f"  {BOLD}Note: DECLINED ✓ = expected decline, system working correctly{RESET}")
    print(f"{'━'*60}\n")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{BOLD}{'━'*60}")
    print(f"  Clearinghouse API Test Suite")
    print(f"  Target: {CCH_URL}")
    print(f"{'━'*60}{RESET}")

    test_jeffs_bank()
    test_tophers_bank()
    test_wild_west()
    test_calibear()
    test_corbin()
    test_josephs_bank()

    print_summary()