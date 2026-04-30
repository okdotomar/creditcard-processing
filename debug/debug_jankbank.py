import requests
payload = {
    "bank":           "JankBank",
    "merchant_name":  "Contact Climbing",
    "merchant_token": "ciAnLzvE",
    "card_holder":    "Jeff Compas",
    "cc_number":      "1234 4321 8939 2329",
    "card_type":      "debit",
    "cvv":            "172",
    "amount":         "12.97",
    "card_zip":       "84790",
    "exp_date":       "06/29",
    "timestamp":      "timestamp"
}
r = requests.post("https://v3k5iwm6zf.execute-api.us-west-2.amazonaws.com/default/processCard", json=payload)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")