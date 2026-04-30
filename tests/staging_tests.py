"""
staging_tests.py
Runs automated tests against the /staging API Gateway endpoint.
Called by the GitHub Actions test-staging.yml workflow.
Exits with code 1 if any critical test fails — this blocks deployment to production.
"""

import requests
import os
import sys
import json
from datetime import datetime

# ── Config from environment variables (set as GitHub secrets) ─────────────────
CCH_URL        = os.environ.get("CCH_STAGING_URL", "")
MERCHANT_NAME  = os.environ.get("MERCHANT_NAME", "Contact Climbing")
MERCHANT_TOKEN = os.environ.get("MERCHANT_TOKEN", "ciAnLzvE")
TIMESTAMP      = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

if not CCH_URL:
    print("FATAL: CCH_STAGING_URL environment variable not set.")
    sys.exit(1)

# ── Results tracking ──────────────────────────────────────────────────────────
passed = []
failed = []


def test(name, payload=None, expected_contains=None, expected_not_contains=None,
         should_reach_bank=True, headers=None):
    """
    Send a request and check the response.
    expected_contains:     string that MUST appear in the response
    expected_not_contains: string that must NOT appear (e.g. 'Server Error')
    should_reach_bank:     if False, we expect a system-level rejection
    """
    print(f"\n  Testing: {name}")
    try:
        resp = requests.post(CCH_URL, json=payload, headers=headers, timeout=15)
        body = resp.text.strip()
        print(f"  Response: {body}")

        fail_reasons = []

        if expected_contains and expected_contains.lower() not in body.lower():
            fail_reasons.append(f"Expected '{expected_contains}' in response, got: {body}")

        if expected_not_contains and expected_not_contains.lower() in body.lower():
            fail_reasons.append(f"Did not expect '{expected_not_contains}' in response, got: {body}")

        if fail_reasons:
            for reason in fail_reasons:
                print(f"  ❌ FAIL: {reason}")
            failed.append({"test": name, "response": body, "reasons": fail_reasons})
        else:
            print(f"  ✅ PASS")
            passed.append({"test": name, "response": body})

    except Exception as e:
        msg = str(e)
        print(f"  ❌ FAIL: Exception — {msg}")
        failed.append({"test": name, "response": "exception", "reasons": [msg]})


def valid_payload(bank, card_type="debit", extra=None):
    """Build a minimal valid payload for a given bank."""
    base = {
        "bank":           bank,
        "merchant_name":  MERCHANT_NAME,
        "merchant_token": MERCHANT_TOKEN,
        "timestamp":      TIMESTAMP,
        "amount":         "25.00",
        "card_type":      card_type,
        "cvv":            "291",
        "exp_date":       "10/27",
        "card_zip":       "84790",
    }
    if extra:
        base.update(extra)
    return base


# ══════════════════════════════════════════════════════════════════════════════
# AUTH TESTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  AUTH TESTS")
print("="*60)

test(
    "Bad merchant token",
    payload={
        "bank": "Jeffs Bank", "merchant_name": MERCHANT_NAME,
        "merchant_token": "BADTOKEN123", "timestamp": TIMESTAMP,
        "amount": "25.00", "card_type": "debit", "cvv": "291",
        "exp_date": "10/27", "card_zip": "84790",
        "cc_number": "4024007175860431", "card_holder": "Olivia Nguyen",
    },
    expected_contains="Not Authorized",
)

test(
    "Missing merchant token",
    payload={
        "bank": "Jeffs Bank", "merchant_name": MERCHANT_NAME,
        "timestamp": TIMESTAMP, "amount": "25.00",
        "card_type": "debit", "cvv": "291", "exp_date": "10/27",
        "card_zip": "84790", "cc_number": "4024007175860431",
        "card_holder": "Olivia Nguyen",
    },
    expected_contains="Invalid Request",
)

test(
    "Unknown merchant name",
    payload={
        "bank": "Jeffs Bank", "merchant_name": "Fake Store XYZ",
        "merchant_token": "faketoken", "timestamp": TIMESTAMP,
        "amount": "25.00", "card_type": "debit", "cvv": "291",
        "exp_date": "10/27", "card_zip": "84790",
        "cc_number": "4024007175860431", "card_holder": "Olivia Nguyen",
    },
    expected_contains="Not Authorized",
)

# ══════════════════════════════════════════════════════════════════════════════
# PAYLOAD VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  PAYLOAD VALIDATION TESTS")
print("="*60)

test(
    "Empty body",
    payload={},
    expected_contains="Invalid Request",
)

test(
    "Missing bank field",
    payload={
        "merchant_name": MERCHANT_NAME, "merchant_token": MERCHANT_TOKEN,
        "timestamp": TIMESTAMP, "amount": "25.00", "card_type": "debit",
        "cvv": "291", "exp_date": "10/27", "card_zip": "84790",
        "cc_number": "4024007175860431", "card_holder": "Olivia Nguyen",
    },
    expected_contains="Invalid Request",
)

test(
    "Missing cc_number",
    payload={
        "bank": "Jeffs Bank", "merchant_name": MERCHANT_NAME,
        "merchant_token": MERCHANT_TOKEN, "timestamp": TIMESTAMP,
        "amount": "25.00", "card_type": "debit", "cvv": "291",
        "exp_date": "10/27", "card_zip": "84790",
        "card_holder": "Olivia Nguyen",
    },
    expected_contains="Invalid Request",
)

test(
    "Missing amount",
    payload={
        "bank": "Jeffs Bank", "merchant_name": MERCHANT_NAME,
        "merchant_token": MERCHANT_TOKEN, "timestamp": TIMESTAMP,
        "card_type": "debit", "cvv": "291", "exp_date": "10/27",
        "card_zip": "84790", "cc_number": "4024007175860431",
        "card_holder": "Olivia Nguyen",
    },
    expected_contains="Invalid Request",
)

test(
    "Unsupported bank name",
    payload={
        "bank": "Bank of Fake", "merchant_name": MERCHANT_NAME,
        "merchant_token": MERCHANT_TOKEN, "timestamp": TIMESTAMP,
        "amount": "25.00", "card_type": "debit", "cvv": "291",
        "exp_date": "10/27", "card_zip": "84790",
        "cc_number": "4024007175860431", "card_holder": "Olivia Nguyen",
    },
    expected_contains="Not Supported",
)

# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH TESTS — JEFFS BANK
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  HAPPY PATH — JEFFS BANK")
print("="*60)

jeff_base = {
    "cc_number": "4024007175860431",
    "card_holder": "Olivia Nguyen",
    "card_zip": "84790",
}

test(
    "Jeffs Bank — valid debit",
    payload={**valid_payload("Jeffs Bank", "debit"), **jeff_base},
    expected_contains="Approved",
    expected_not_contains="Server Error",
)

test(
    "Jeffs Bank — valid deposit",
    payload={**valid_payload("Jeffs Bank", "deposit"), **jeff_base},
    expected_contains="Approved",
    expected_not_contains="Server Error",
)

# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH TESTS — TOPHERS BANK
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  HAPPY PATH — TOPHERS BANK")
print("="*60)

test(
    "Tophers Bank — valid debit",
    payload={
        **valid_payload("Tophers Bank", "debit"),
        "cc_number":   "4916338506082839",
        "card_holder": "Diana Osei",
        "cvv":         "a4d0f625",
        "exp_date":    "2028-06",
    },
    expected_contains="Approved",
    expected_not_contains="Server Error",
)

# ══════════════════════════════════════════════════════════════════════════════
# HAPPY PATH TESTS — JOSEPHS BANK
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  HAPPY PATH — JOSEPHS BANK")
print("="*60)

test(
    "Josephs Bank — valid debit",
    payload={
        **valid_payload("Josephs Bank", "debit"),
        "cc_number":          "4111111111111042",
        "merchant_bank_acct": "ACCT100042",
        "card_holder":        "Madison Bell",
        "card_zip":           "63102",
        "cvv":                "147",
        "exp_date":           "11/26",
    },
    expected_contains="Approved",
    expected_not_contains="Server Error",
)

# ══════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  EDGE CASES")
print("="*60)

test(
    "Jeffs Bank — bad card number (should decline not crash)",
    payload={
        **valid_payload("Jeffs Bank", "debit"),
        "cc_number":   "0000000000000000",
        "card_holder": "Fake Person",
        "card_zip":    "00000",
    },
    expected_not_contains="Server Error",
)

test(
    "Jeffs Bank — negative amount",
    payload={
        **valid_payload("Jeffs Bank", "debit"),
        "cc_number":   "4024007175860431",
        "card_holder": "Olivia Nguyen",
        "card_zip":    "84790",
        "amount":      "-50.00",
    },
    expected_not_contains="Server Error",
)

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
total = len(passed) + len(failed)
print("\n" + "="*60)
print(f"  STAGING TEST RESULTS: {len(passed)}/{total} passed")
print("="*60)

if failed:
    print("\n  ❌ FAILED TESTS:")
    for f in failed:
        print(f"\n    Test:     {f['test']}")
        print(f"    Response: {f['response']}")
        for reason in f['reasons']:
            print(f"    Reason:   {reason}")
    print(f"\n  {len(failed)} test(s) failed — blocking deployment to production.\n")
    sys.exit(1)
else:
    print("\n  ✅ All tests passed — safe to deploy to production.\n")
    sys.exit(0)
