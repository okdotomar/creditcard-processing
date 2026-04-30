"""
merchant_simulator_500.py
Sends 500+ transactions across 5 banks and 50 real St. George merchants.
Run: python3 merchant_simulator_500.py
"""

import requests
import random
import time
from datetime import datetime, timezone

CCH_URL = "https://v3k5iwm6zf.execute-api.us-west-2.amazonaws.com/default/processCard"

# ── 50 Real merchants from the class merchant table ───────────────────────────
MERCHANTS = [
    {"merchant_name": "Tifinys Creperie", "merchant_token": "xGl2zcPA"},
    {"merchant_name": "Dutchmans Market", "merchant_token": "hIhksw4s"},
    {"merchant_name": "Sweet Rolled Tacos", "merchant_token": "W71AnrQu"},
    {"merchant_name": "Cafe Rio", "merchant_token": "GMuOikG4"},
    {"merchant_name": "Judds Store", "merchant_token": "U8et7kOX"},
    {"merchant_name": "Cliffside Restaurant", "merchant_token": "hiKzn4GE"},
    {"merchant_name": "Bear Paw Cafe", "merchant_token": "0PDOt87g"},
    {"merchant_name": "Sues Pet Castle", "merchant_token": "CUQpt2hi"},
    {"merchant_name": "Contact Climbing", "merchant_token": "ciAnLzvE"},
    {"merchant_name": "Fiiz Drinks", "merchant_token": "xRcMVZt5"},
    {"merchant_name": "Nielsens Frozen Custard", "merchant_token": "nvfeNWrn"},
    {"merchant_name": "Viva Chicken", "merchant_token": "xPOMrAu2"},
    {"merchant_name": "Riggattis Pizza", "merchant_token": "9rhu9xjT"},
    {"merchant_name": "Tagg and Go Car Wash", "merchant_token": "9e25AhO8"},
    {"merchant_name": "gigi gelati", "merchant_token": "IXNDePt6"},
    {"merchant_name": "Costco", "merchant_token": "DZXBV92s"},
    {"merchant_name": "Mortys Cafe", "merchant_token": "FjPVlUR4"},
    {"merchant_name": "Bishops Grill", "merchant_token": "szZRz8oe"},
    {"merchant_name": "Veyo Pies", "merchant_token": "WjY3Fj1L"},
    {"merchant_name": "Angelicas Mexican Grill", "merchant_token": "sIwVMwzF"},
    {"merchant_name": "Xetava Gardens Cafe", "merchant_token": "ri47FJqo"},
    {"merchant_name": "Benjas Thai Sushi", "merchant_token": "febuSu6O"},
    {"merchant_name": "FeelLove Coffee", "merchant_token": "MDSHVulj"},
    {"merchant_name": "Teriyaki Grill", "merchant_token": "qi3vvwtv"},
    {"merchant_name": "Desert Rat", "merchant_token": "GgnRlH67"},
    {"merchant_name": "Red Rock Roasting Co", "merchant_token": "8aeu90dy"},
    {"merchant_name": "Pica Rica BBQ", "merchant_token": "vdMGy7IJ"},
    {"merchant_name": "Georges Corner Restaurant", "merchant_token": "rGtsiE0e"},
    {"merchant_name": "Painted Pony", "merchant_token": "QFhahv4K"},
    {"merchant_name": "Sakura Japanese Steakhouse", "merchant_token": "5yGuXhvV"},
    {"merchant_name": "Pizza Factory", "merchant_token": "PPBqnohw"},
    {"merchant_name": "Big Shots Golf", "merchant_token": "1wgN5E1t"},
    {"merchant_name": "Zion Brewery", "merchant_token": "RTwJShn1"},
    {"merchant_name": "Red Rock Bicycle", "merchant_token": "9KqkBtAn"},
    {"merchant_name": "Sol Foods", "merchant_token": "m39ShvHl"},
    {"merchant_name": "Tommys Express Car Wash", "merchant_token": "vd8vwysf"},
    {"merchant_name": "Arctic Circle", "merchant_token": "OCmngQJ4"},
    {"merchant_name": "Costa Vida", "merchant_token": "AzFM4BXv"},
    {"merchant_name": "Utah Tech Campus Bookstore", "merchant_token": "ISDKxbCF"},
    {"merchant_name": "Swig", "merchant_token": "GVkgKk5O"},
    {"merchant_name": "Smiths", "merchant_token": "TlAnbSU1"},
    {"merchant_name": "Irmitas Casita", "merchant_token": "9uPWL3S7"},
    {"merchant_name": "Cappellettis", "merchant_token": "U55VhFuk"},
    {"merchant_name": "Zion Outfitters", "merchant_token": "RVKwjpQs"},
    {"merchant_name": "Lins", "merchant_token": "zkkn0n6M"},
    {"merchant_name": "Station 2 Bar", "merchant_token": "EoAv62Cr"},
    {"merchant_name": "Taco Amigo", "merchant_token": "BsM86wrq"},
    {"merchant_name": "Wood Ash Rye", "merchant_token": "QAJr8xhB"},
    {"merchant_name": "Walmart", "merchant_token": "260fZojB"},
    {"merchant_name": "Rancheritos Mexican Food", "merchant_token": "g0EleGLo"},
]

# ── 5 banks ───────────────────────────────────────────────────────────────────
BANK_ACCOUNTS = [
    # Jeffs Bank
    {"bank": "Jeffs Bank", "card_type": "debit",
     "cc_number": "4024007175860431", "card_holder": "Olivia Nguyen",
     "card_zip": "84790", "cvv": "291", "exp_date": "10/27"},
    {"bank": "Jeffs Bank", "card_type": "debit",
     "cc_number": "4556737586899855", "card_holder": "Ethan Lee",
     "card_zip": "84015", "cvv": "033", "exp_date": "07/26"},
    {"bank": "Jeffs Bank", "card_type": "credit",
     "cc_number": "4532118559116467", "card_holder": "Ava Jensen",
     "card_zip": "84770", "cvv": "412", "exp_date": "03/28"},
    {"bank": "Jeffs Bank", "card_type": "credit",
     "cc_number": "4916338506084064", "card_holder": "Liam Carter",
     "card_zip": "84770", "cvv": "891", "exp_date": "11/27"},
    {"bank": "Jeffs Bank", "card_type": "deposit",
     "cc_number": "4539578763621290", "card_holder": "Noah Ramirez",
     "card_zip": "84770", "cvv": "123", "exp_date": "06/28"},

    # Tophers Bank
    {"bank": "Tophers Bank", "card_type": "debit",
     "cc_number": "4916338506082839", "card_holder": "Diana Osei",
     "card_zip": "84770", "cvv": "a4d0f625", "exp_date": "2028-06"},
    {"bank": "Tophers Bank", "card_type": "debit",
     "cc_number": "4556737586896483", "card_holder": "Samuel Nguyen",
     "card_zip": "84770", "cvv": "b3c2d891", "exp_date": "2027-04"},
    {"bank": "Tophers Bank", "card_type": "credit",
     "cc_number": "5425233430109911", "card_holder": "Elise Beaumont",
     "card_zip": "84770", "cvv": "a7d6f281", "exp_date": "2026-03"},
    {"bank": "Tophers Bank", "card_type": "deposit",
     "cc_number": "4916338506089903", "card_holder": "TechNova Solutions LLC",
     "card_zip": "84770", "cvv": "c9f2b445", "exp_date": "2027-09"},

    # Josephs Bank
    {"bank": "Josephs Bank", "card_type": "debit",
     "cc_number": "4111111111111042", "card_holder": "Madison Bell",
     "card_zip": "63102", "cvv": "147", "exp_date": "11/26",
     "merchant_bank_acct": "ACCT100042"},
    {"bank": "Josephs Bank", "card_type": "debit",
     "cc_number": "4111111111111038", "card_holder": "Avery Rogers",
     "card_zip": "78702", "cvv": "654", "exp_date": "07/28",
     "merchant_bank_acct": "ACCT100038"},
    {"bank": "Josephs Bank", "card_type": "credit",
     "cc_number": "4111111111111020", "card_holder": "Evelyn Hill",
     "card_zip": "30301", "cvv": "321", "exp_date": "05/27",
     "merchant_bank_acct": "ACCT100020"},
    {"bank": "Josephs Bank", "card_type": "credit",
     "cc_number": "4111111111111015", "card_holder": "Alexander Young",
     "card_zip": "77001", "cvv": "852", "exp_date": "09/27",
     "merchant_bank_acct": "ACCT100015"},

    # CaliBear Bank
    {"bank": "Calibear Bank", "card_type": "debit",
     "cc_number": "9594406409097439", "card_holder": "Michael Abraham",
     "card_zip": "84770", "cvv": "000", "exp_date": "12/27"},
    {"bank": "Calibear Bank", "card_type": "credit",
     "cc_number": "2104709521456232", "card_holder": "Michael Abraham",
     "card_zip": "84770", "cvv": "000", "exp_date": "12/27"},
    {"bank": "Calibear Bank", "card_type": "debit",
     "cc_number": "2474517123685160", "card_holder": "Broxton Alexander",
     "card_zip": "84770", "cvv": "000", "exp_date": "12/27"},
    {"bank": "Calibear Bank", "card_type": "deposit",
     "cc_number": "4965137098593529", "card_holder": "David Dipalo-Gross",
     "card_zip": "84770", "cvv": "000", "exp_date": "12/27"},

    # Corbin Bank
    {"bank": "Corbin Bank", "card_type": "debit",
     "cc_number": "4947970898951263", "card_holder": "David Dipalo-Gross",
     "card_zip": "84001", "cvv": "359", "exp_date": "09/27"},
    {"bank": "Corbin Bank", "card_type": "debit",
     "cc_number": "4701775649281048", "card_holder": "Broxton Alexander",
     "card_zip": "78201", "cvv": "188", "exp_date": "01/28"},
    {"bank": "Corbin Bank", "card_type": "credit",
     "cc_number": "4947970898950959", "card_holder": "Austin Rager",
     "card_zip": "73102", "cvv": "359", "exp_date": "09/27"},
    {"bank": "Corbin Bank", "card_type": "credit",
     "cc_number": "4701775649286398", "card_holder": "Nathan Monroy",
     "card_zip": "78201", "cvv": "188", "exp_date": "01/28"},
]

AMOUNTS = [
    "5.99", "12.50", "24.99", "37.00", "49.95", "63.20",
    "75.00", "88.49", "102.00", "150.75", "200.00", "250.00",
    "9.99", "18.00", "33.50", "45.00", "99.99", "125.00",
    "15.00", "22.75", "55.00", "78.00", "110.00", "175.00",
]


def send_transaction(merchant, account, amount):
    payload = {
        "merchant_name":  merchant["merchant_name"],
        "merchant_token": merchant["merchant_token"],
        "timestamp":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "amount":         amount,
        **{k: v for k, v in account.items()},
    }
    try:
        resp   = requests.post(CCH_URL, json=payload, timeout=15)
        result = resp.text.strip()
        icon   = "✅" if "Approved" in result else ("⚠️" if "Declined" in result else "❌")
        print(f"{icon} [{merchant['merchant_name'][:18]:18}] "
              f"{account['bank']:15} | ${amount:>7} | {result}")
        return result
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        return "Error"


def run(total=510):
    bank_names = list(set(a["bank"] for a in BANK_ACCOUNTS))
    print(f"\nSending {total} transactions")
    print(f"Merchants: {len(MERCHANTS)} | Banks: {len(bank_names)}")
    print(f"Banks: {', '.join(sorted(bank_names))}\n")
    print(f"{'─'*75}")

    counts      = {"Approved": 0, "Declined": 0, "Error": 0}
    bank_counts = {b: 0 for b in bank_names}

    for i in range(total):
        merchant = random.choice(MERCHANTS)
        account  = random.choice(BANK_ACCOUNTS)
        amount   = random.choice(AMOUNTS)

        result = send_transaction(merchant, account, amount)

        if "Approved"  in result: counts["Approved"]  += 1
        elif "Declined" in result: counts["Declined"] += 1
        else:                      counts["Error"]    += 1

        bank_counts[account["bank"]] += 1
        time.sleep(0.2)

    print(f"\n{'─'*75}")
    print(f"  RESULTS")
    print(f"{'─'*75}")
    print(f"  Total:    {total}")
    print(f"  Approved: {counts['Approved']}")
    print(f"  Declined: {counts['Declined']}")
    print(f"  Errors:   {counts['Error']}")
    print(f"\n  Transactions per bank:")
    for bank, count in sorted(bank_counts.items(), key=lambda x: -x[1]):
        print(f"    {bank:25} {count}")
    print(f"\n  Done! Check your TransactionLog table in DynamoDB.")


if __name__ == "__main__":
    run(510)