import json
import boto3
import urllib3
from datetime import datetime, timezone

# ── AWS ───────────────────────────────────────────────────────────────────────
dynamodb     = boto3.resource('dynamodb')
merchant_tbl = dynamodb.Table('Merchant')
log_tbl      = dynamodb.Table('Transaction')
http         = urllib3.PoolManager()

# ── Bank Config Map ───────────────────────────────────────────────────────────
BANKS = {
    "jeffs_bank": {
        "url": "https://9q350g4063.execute-api.us-west-2.amazonaws.com/default/handleTransaction",
        "auth_style": "body",
        "auth": {"cch_name": "rodriguez_cch", "cch_token": "3RhyMG7g"},
        "txn_style": "debit_credit_deposit",
        "amount_type": "string",
        "field_map": {
            "cc_num":    "card_num",
            "cardholder":"card_holder",
            "card_zip":  "card_zip",
            "cvv":       "cvv",
            "exp_date":  "exp_date",
            "merchant":  "merchant",
            "amount":    "amount",
            "timestamp": "timestamp",
            "txn_type":  "txn_type",
            "cch_name":  "cch_name",
            "cch_token": "cch_token",
        }
    },
    "tophers_bank": {
        "url": "https://lp4uqktsqg.execute-api.us-west-2.amazonaws.com/default/doRequest",
        "auth_style": "body",
        "auth": {"cch_name": "orodriguez_cch", "cch_token": "E4uW5cJh"},
        "txn_style": "withdrawal_bool",
        "amount_type": "number",
        "field_map": {
            "cc_num":     "card_number",
            "cvv":        "cvv",
            "exp_date":   "exp_date",   # will be converted to YYYY-MM in call_bank
            "merchant":   "merchant_name",
            "amount":     "amount",
            "txn_type":   "transaction_type",
            "withdrawal": "withdrawal",
            "cch_name":   "cch_name",
            "cch_token":  "cch_token",
        }
    },
    "wild_west": {
        "url": "https://l25ft7pzu5wpwm3xtskoiks6rm0javto.lambda-url.us-west-2.on.aws/",
        "auth_style": "body",
        "auth": {"cch_name": "rodriguez_cch", "cch_token": "x2T9vB5W"},
        "txn_style": "withdrawal_deposit",
        "amount_type": "string",
        "field_map": {
            "account_num": "account_number",   # Wild West uses merchant_bank_acct (10-digit)
            "cardholder":  "account_holder_name",
            "card_type":   "card_type",
            "amount":      "amount",
            "txn_type":    "transaction_type",
            "cch_name":    "cch_name",
            "cch_token":   "cch_token",
        }
    },
    "calibear": {
        "url": "https://api.calibear.credit/transaction/",
        "auth_style": "header",
        "auth": {
            "header_key":       "x-api-key",
            "header_value":     "credential_token_przhbg0otelkw2s3z9xwgln",
            "clearinghouse_id": "CH-5trbskyjevge",
        },
        "txn_style": "withdrawal_deposit",
        "amount_type": "number",
        "field_map": {
            "cc_num":           "card_number",
            "merchant":         "merchant_name",
            "amount":           "amount",
            "txn_type":         "transaction_type",
            "clearinghouse_id": "clearinghouse_id",
        }
    },
    "corbin": {
        "url": "https://xbu6ixwga4.execute-api.us-west-2.amazonaws.com/default/handleTransaction",
        "auth_style": "header",
        "auth": {"username": "rodriguez_cch", "password": "x2T9vB5W"},
        "txn_style": "withdrawal_deposit",
        "amount_type": "string",
        "field_map": {
            "cc_num":    "account_num",
            "cvv":       "cvv",
            "exp_date":  "exp_date",
            "card_type": "card_type",
            "amount":    "amount",
            "txn_type":  "transaction_type",
        }
    },
    "josephs_bank": {
        "url": "https://yt1i4wstmb.execute-api.us-west-2.amazonaws.com/default/transact",
        "auth_style": "body",
        "auth": {"cch_name": "orodriguez", "cch_token": "Ao3iHhMIJzL6VxPALFJ1W7rb4Ma06oRi"},
        "txn_style": "debit_credit_deposit",
        "amount_type": "string",
        "field_map": {
            "cc_num":      "card_num",
            "account_num": "account_num",  # Joseph needs ACCT-style account number
            "cvv":         "cvv",
            "exp_date":    "exp_date",
            "merchant":    "merchant",
            "amount":      "amount",
            "txn_type":    "type",
            "cch_name":    "cch_name",
            "cch_token":   "cch_token",
        }
    },
}

BANK_ALIASES = {
    "jeffs bank":            "jeffs_bank",
    "jeff's bank":           "jeffs_bank",
    "tophers bank":          "tophers_bank",
    "topher's bank":         "tophers_bank",
    "wild west bank":        "wild_west",
    "wild west":             "wild_west",
    "calibear":              "calibear",
    "calibear bank":         "calibear",
    "calibear credit union": "calibear",
    "corbin bank":           "corbin",
    "corbin":                "corbin",
    "josephs bank":          "josephs_bank",
    "joseph's bank":         "josephs_bank",
    "jank bank":             "josephs_bank",
}


# ── Field Formatters ──────────────────────────────────────────────────────────
def format_exp_date_for_topher(exp_date):
    """Convert MM/YY or MM/YYYY to YYYY-MM format that Topher's accounts store."""
    try:
        parts = exp_date.strip().split("/")
        month = parts[0].zfill(2)
        year  = parts[1]
        if len(year) == 2:
            year = "20" + year
        return f"{year}-{month}"
    except Exception:
        return exp_date  # return as-is if already in correct format or unparseable


def clean_card_number(cc_num):
    """Strip spaces and dashes from card numbers."""
    return cc_num.replace(" ", "").replace("-", "") if cc_num else ""


# ── Transaction Type Resolver ─────────────────────────────────────────────────
def resolve_txn_fields(bank_cfg, card_type):
    card_type = card_type.lower().strip()
    style     = bank_cfg["txn_style"]
    fields    = {}

    if style == "debit_credit_deposit":
        fields["txn_type"] = "deposit" if card_type == "deposit" else card_type

    elif style == "withdrawal_deposit":
        fields["txn_type"]  = "deposit" if card_type == "deposit" else "withdrawal"
        fields["card_type"] = "debit" if card_type in ("debit", "deposit") else "credit"

    elif style == "withdrawal_bool":
        if card_type == "deposit":
            fields["txn_type"]   = "debit"
            fields["withdrawal"] = False
        elif card_type == "credit":
            fields["txn_type"]   = "credit"
            fields["withdrawal"] = True   # credit purchase = withdrawal from credit line
        else:
            fields["txn_type"]   = "debit"
            fields["withdrawal"] = True

    return fields


# ── Generic Bank Caller ───────────────────────────────────────────────────────
def call_bank(bank_key, bank_cfg, inbound):
    card_type  = (inbound.get("card_type") or "").lower().strip()
    cc_num     = clean_card_number(inbound.get("cc_number") or inbound.get("cc_num", ""))
    cardholder = inbound.get("card_holder") or inbound.get("customer_name", "")
    amount_raw = inbound.get("amount", "0")
    exp_date   = inbound.get("exp_date", "")
    field_map  = bank_cfg["field_map"]
    auth       = bank_cfg["auth"]
    auth_style = bank_cfg["auth_style"]

    # Topher stores exp_date as YYYY-MM — convert before sending
    if bank_key == "tophers_bank":
        exp_date = format_exp_date_for_topher(exp_date)

    txn_fields = resolve_txn_fields(bank_cfg, card_type)
    amount     = float(amount_raw) if bank_cfg["amount_type"] == "number" else str(amount_raw)

    # merchant_bank_acct is the correct account number for Wild West and Joseph
    merchant_bank_acct = inbound.get("merchant_bank_acct") or cc_num

    internal = {
        "cc_num":      cc_num,
        "account_num": merchant_bank_acct,
        "cardholder":  cardholder,
        "card_zip":    inbound.get("card_zip", ""),
        "cvv":         inbound.get("cvv", ""),
        "exp_date":    exp_date,
        "merchant":    inbound.get("merchant_name", ""),
        "amount":      amount,
        "timestamp":   inbound.get("timestamp", ""),
        "card_type":   "debit" if card_type in ("debit", "deposit") else "credit",
        **txn_fields,
    }

    if auth_style == "body":
        internal.update({k: v for k, v in auth.items() if k not in ("header_key", "header_value")})

    # clearinghouse_id always goes in the body even when auth_style is "header" (CaliBear)
    if "clearinghouse_id" in auth:
        internal["clearinghouse_id"] = auth["clearinghouse_id"]

    payload = {}
    for our_key, their_key in field_map.items():
        if our_key in internal:
            payload[their_key] = internal[our_key]

    headers = {"Content-Type": "application/json"}
    if auth_style == "header":
        if "header_key" in auth:
            headers[auth["header_key"]] = auth["header_value"]
        if "username" in auth:
            headers["username"] = auth["username"]
            headers["password"] = auth["password"]

    try:
        resp = http.request("POST", bank_cfg["url"], body=json.dumps(payload), headers=headers)
        try:
            body = json.loads(resp.data.decode("utf-8"))
        except Exception:
            body = {"message": resp.data.decode("utf-8")}
        return resp.status, body
    except Exception as e:
        return 500, {"message": str(e)}


# ── Response Normalizer ───────────────────────────────────────────────────────
def normalize_response(bank_key, status_code, body):
    if isinstance(body, dict) and isinstance(body.get("body"), str):
        try:
            body = json.loads(body["body"])
        except Exception:
            pass

    msg = ""
    if isinstance(body, dict):
        msg = body.get("message") or body.get("outcome") or str(body)
    else:
        msg = str(body)

    msg_lower = msg.lower()
    print(f"[{bank_key}] HTTP={status_code} msg={msg}")

    if status_code in (200, 202):
        if any(w in msg_lower for w in ("accepted", "approved", "successful", "completed")):
            return "Approved."
        if isinstance(body, dict) and body.get("outcome") == "accepted":
            return "Approved."

    if "insufficient" in msg_lower:    return "Declined - Insufficient Funds."
    if "credit limit" in msg_lower:    return "Declined - Credit Limit Exceeded."
    if "daily limit"  in msg_lower:    return "Declined - Daily Limit Exceeded."
    if "frozen"       in msg_lower:    return "Declined - Account Frozen."
    if "closed"       in msg_lower:    return "Declined - Account Closed."
    if "overdrawn"    in msg_lower:    return "Declined - Account Overdrawn."
    if "declined"     in msg_lower:    return "Declined - Card Not Valid."

    if status_code == 401:             return "Declined - Server Error."
    if status_code in (400, 422, 502): return "Declined - Invalid Request."
    if status_code in (402, 403):      return "Declined - Insufficient Funds."
    if status_code == 404:             return "Declined - Card Not Valid."

    return "Declined - Server Error."


# ── Logging ───────────────────────────────────────────────────────────────────
def write_log(merchant_name, bank_name, cc_num, amount, status):
    try:
        last_four = str(cc_num)[-4:] if cc_num else "0000"
        log_tbl.put_item(Item={
            "transaction_id": f"{merchant_name}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            "merchant_name":  merchant_name or "Unknown",
            "bank_name":      bank_name or "Unknown",
            "last_four":      last_four,
            "amount":         str(amount or "0.00"),
            "datetime":       datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status":         status
        })
    except Exception as e:
        print(f"[LOG ERROR] {str(e)}")


# ── Helpers ───────────────────────────────────────────────────────────────────
def respond(message):
    return {"statusCode": 200, "headers": {"Content-Type": "text/plain"}, "body": message}


def authenticate_merchant(name, token):
    if not name or not token:
        return False
    try:
        return 'Item' in merchant_tbl.get_item(Key={'Name': name, 'Token': token})
    except Exception:
        return False


def validate(data):
    required = ["bank", "merchant_name", "merchant_token", "card_type", "cvv", "amount", "exp_date"]
    for field in required:
        if not data.get(field):
            return False
    return bool(data.get("cc_number") or data.get("cc_num"))


# ── Main Handler ──────────────────────────────────────────────────────────────
def lambda_handler(event, context):
    try:
        data = json.loads(event['body']) if 'body' in event else event
    except Exception:
        return respond("Declined - Invalid Request.")

    merchant_name = data.get('merchant_name')
    bank_name_raw = data.get('bank', '')
    cc_num        = data.get('cc_number') or data.get('cc_num')
    amount        = data.get('amount')

    if not validate(data):
        write_log(merchant_name, bank_name_raw, cc_num, amount, "Error")
        return respond("Declined - Invalid Request.")

    if not authenticate_merchant(merchant_name, data.get('merchant_token')):
        write_log(merchant_name, bank_name_raw, cc_num, amount, "Error")
        return respond("Merchant Not Authorized.")

    bank_key = BANK_ALIASES.get(bank_name_raw.lower().strip())
    bank_cfg = BANKS.get(bank_key)
    if not bank_cfg:
        write_log(merchant_name, bank_name_raw, cc_num, amount, "Error")
        return respond("Bank Not Supported.")

    status_code, body = call_bank(bank_key, bank_cfg, data)
    result            = normalize_response(bank_key, status_code, body)

    log_status = "Approved" if "Approved" in result else ("Declined" if "Declined" in result else "Error")
    write_log(merchant_name, bank_name_raw, cc_num, amount, log_status)
    return respond(result)