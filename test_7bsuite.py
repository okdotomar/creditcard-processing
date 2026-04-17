import requests
import datetime

url = "https://ymvzi3kjlej4d2k5m2njbzpnau0fzows.lambda-url.us-west-2.on.aws/"

timestamp = str(datetime.datetime.now())

test_cases = [
    # ── MERCHANT AUTH ────────────────────────────────────────────
    {
        "description": "✅ Valid merchant - Bear Paw Cafe",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Accepted"
    },
    {
        "description": "❌ Wrong merchant token",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "wrongtoken",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Fake merchant name",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Fake Store",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Missing merchant token",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_bank": "Jeffs Bank",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Unsupported bank",
        "payload": {
            "bank": "Fake Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Fake Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Bank Not Supported"
    },

    # ── ACCEPTED TRANSACTIONS ────────────────────────────────────
    {
        "description": "✅ Valid debit - Benjamin Hill small amount",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Accepted"
    },
    {
        "description": "✅ Valid credit - Liam Carter small amount",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Costco",
            "merchant_token": "DZXBV92s",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532756279624064",
            "customer_name": "Liam Carter",
            "cc_num": "4532756279624064",
            "card_type": "credit",
            "cvv": "648",
            "amount": "5.00",
            "card_zip": "84770",
            "exp_date": "04/28",
            "timestamp": timestamp
        },
        "expected": "Accepted"
    },
    {
        "description": "✅ Valid debit - Mia Thompson",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Costco",
            "merchant_token": "DZXBV92s",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4485921786505210",
            "customer_name": "Mia Thompson",
            "cc_num": "4485921786505210",
            "card_type": "debit",
            "cvv": "512",
            "amount": "10.00",
            "card_zip": "84101",
            "exp_date": "03/29",
            "timestamp": timestamp
        },
        "expected": "Accepted"
    },

    # ── DECLINED TRANSACTIONS ────────────────────────────────────
    {
        "description": "❌ Insufficient funds - Noah Ramirez only has $82.19",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4716461583322103",
            "customer_name": "Noah Ramirez",
            "cc_num": "4716461583322103",
            "card_type": "debit",
            "cvv": "907",
            "amount": "100.00",
            "card_zip": "84790",
            "exp_date": "12/27",
            "timestamp": timestamp
        },
        "expected": "Declined - Insufficient Funds."
    },
    {
        "description": "❌ Insufficient funds - Ethan Lee only has $14.02",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4556737586899855",
            "customer_name": "Ethan Lee",
            "cc_num": "4556737586899855",
            "card_type": "debit",
            "cvv": "033",
            "amount": "50.00",
            "card_zip": "84015",
            "exp_date": "07/26",
            "timestamp": timestamp
        },
        "expected": "Accepted."
    },
    {
        "description": "❌ Bad CVV",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "999",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Invalid account info"
    },
    {
        "description": "❌ Bad zip code",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "00000",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Invalid account info"
    },
    {
        "description": "❌ Bad expiration date",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "4532115610653722",
            "customer_name": "Benjamin Hill",
            "cc_num": "4532115610653722",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "01/20",
            "timestamp": timestamp
        },
        "expected": "Invalid account info"
    },
    {
        "description": "❌ Bad account number - Do Not Honor",
        "payload": {
            "bank": "Jeffs Bank",
            "merchant_name": "Bear Paw Cafe",
            "merchant_token": "0PDOt87g",
            "merchant_bank": "Jeffs Bank",
            "merchant_bank_acct": "0000000000000000",
            "customer_name": "Benjamin Hill",
            "cc_num": "0000000000000000",
            "card_type": "debit",
            "cvv": "225",
            "amount": "5.00",
            "card_zip": "84003",
            "exp_date": "02/27",
            "timestamp": timestamp
        },
        "expected": "Invalid account info"
    },
]

passed = 0
failed = 0

print("=" * 60)
print("8A BANK API TEST SUITE")
print("=" * 60)

for test in test_cases:
    result = requests.post(url, json=test["payload"])
    response_text = result.text.strip()

    if test["expected"].lower() in response_text.lower():
        status = "PASS"
        passed += 1
    else:
        status = "FAIL"
        failed += 1

    print(f"\n[{status}] {test['description']}")
    if status == "FAIL":
        print(f"      Expected : {test['expected']}")
        print(f"      Got      : {response_text}")

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 60)