import requests

url = "https://kkivhurgxtbgiccq7iwavrejnu0ctavz.lambda-url.us-west-2.on.aws/ "  # <-- replace with your 7A URL

test_cases = [
    {
        "description": "✅ Valid merchant - Bear Paw Cafe",
        "payload": {"merchant_name": "Bear Paw Cafe", "merchant_token": "0PDOt87g"},
        "expected": "Merchant Authorized"
    },
    {
        "description": "✅ Valid merchant - Costco",
        "payload": {"merchant_name": "Costco", "merchant_token": "DZXBV92s"},
        "expected": "Merchant Authorized"
    },
    {
        "description": "❌ Wrong token",
        "payload": {"merchant_name": "Bear Paw Cafe", "merchant_token": "wrongtoken"},
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Fake merchant name",
        "payload": {"merchant_name": "Fake Store", "merchant_token": "0PDOt87g"},
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Both wrong",
        "payload": {"merchant_name": "Fake Store", "merchant_token": "wrongtoken"},
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Missing token",
        "payload": {"merchant_name": "Bear Paw Cafe"},
        "expected": "Merchant Not Authorized"
    },
    {
        "description": "❌ Empty strings",
        "payload": {"merchant_name": "", "merchant_token": ""},
        "expected": "Merchant Not Authorized"
    },
]

passed = 0
failed = 0

print("=" * 55)
print("MERCHANT AUTHENTICATION TEST SUITE")
print("=" * 55)

for test in test_cases:
    result = requests.post(url, json=test["payload"])
    response_text = result.text.strip()
    
    # Check if expected string is anywhere in the response
    if test["expected"] in response_text:
        status = "PASS"
        passed += 1
    else:
        status = "FAIL"
        failed += 1
    
    print(f"\n[{status}] {test['description']}")
    if status == "FAIL":
        print(f"      Expected : {test['expected']}")
        print(f"      Got      : {response_text}")

print("\n" + "=" * 55)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 55)