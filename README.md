# Credit Card Clearinghouse

A serverless credit card processing API built on AWS Lambda. The system acts as a **clearinghouse** — it sits between point-of-sale merchants and multiple bank APIs, authenticating merchants, routing transactions to the correct bank, normalizing responses, and logging every transaction.

---

## How It Works

```
Merchant POS  →  API Gateway  →  Lambda (processCard)  →  Bank API
                                        ↕
                                   DynamoDB
                              (Merchants · Transactions)
```

1. A merchant sends a JSON transaction payload to the API Gateway endpoint.
2. The Lambda validates the request and authenticates the merchant against DynamoDB.
3. The correct bank is looked up from a configuration map and the transaction is forwarded using that bank's specific auth style and field schema.
4. The bank's response is normalized into a consistent result string (`Approved.` or a specific `Declined - ...` reason).
5. Every transaction is logged to DynamoDB with masked card data.

---

## Features

- **Multi-bank routing** — integrates with 6 banks, each with a different API contract (field names, auth styles, transaction type enums)
- **Merchant authentication** — name + token verification against DynamoDB before any transaction is forwarded
- **Response normalization** — maps each bank's varied response formats into a unified set of outcomes
- **Transaction logging** — every request is written to DynamoDB with only the last 4 digits of the card number (PCI-aligned)
- **Input validation** — rejects malformed or incomplete payloads before they reach any bank
- **Reporting** — Excel report generator that reads DynamoDB exports and produces summary + pie charts
- **CI/CD pipeline** — automated staging deploy and test gate on every push; production only receives a version that passed all staging tests

---

## Project Structure

```
.
├── lambda_function.py            # Main Lambda handler — routing, auth, logging
├── merchant_simulator.py         # Simulates transactions for manual testing
├── merchant_simulator_500.py     # Sends 500+ transactions across 5 banks and 50 merchants
├── build_report.py               # Generates an Excel report from a DynamoDB CSV export
├── spam-cchs.py                  # Continuously sends transactions to multiple endpoints (bulk testing)
├── bio.py                        # Developer bio
│
├── tests/
│   ├── staging_tests.py          # Automated CI test suite — runs against the staging endpoint
│   ├── testBanks.py              # Integration tests for verifying each bank API
│   ├── test_7asuite.py           # Test suite 7A
│   └── test_7bsuite.py           # Test suite 7B
│
├── debug/
│   ├── debugBanks.py             # Calls each bank directly to inspect raw responses
│   ├── debug_corbin.py           # Corbin Bank-specific debug helper
│   └── debug_jankbank.py         # JankBank-specific debug helper
│
├── csv/
│   ├── merchants.csv             # Registered merchants (name + token)
│   ├── jeffs_bank_accounts.csv   # Jeff's Bank test accounts
│   ├── tophers_bank_accounts.csv # Topher's Bank test accounts
│   ├── calibear_bank_accounts.csv
│   ├── corbin_bank_accounts.csv
│   ├── joseph_bank_accounts.csv
│   ├── jankbank_bank_accounts.csv
│   ├── barrett_bank_accounts.csv
│   └── deanna_bank_accounts.csv
│
├── charts/
│   ├── BurndownChart.pdf         # Sprint burndown chart
│   └── Diagrams.pdf              # System architecture diagrams
│
├── DBDesign.md                   # DynamoDB schema design notes
├── requirements.md               # Original project requirements document
└── .github/workflows/
    ├── deploy-staging.yml        # Deploys Lambda on push to main
    ├── test-staging.yml          # Runs staging_tests.py against the staging alias
    └── deploy-production.yml     # Promotes staging → production if tests pass
```

---

## API

**Endpoint:** `POST /processCard`

### Request Body

```json
{
  "bank":            "Jeffs Bank",
  "merchant_name":   "Bear Paw Cafe",
  "merchant_token":  "<token>",
  "cc_number":       "4024007175860431",
  "card_holder":     "Olivia Nguyen",
  "card_type":       "debit",
  "cvv":             "291",
  "exp_date":        "10/27",
  "card_zip":        "84790",
  "amount":          "25.00",
  "timestamp":       "2025-01-01T00:00:00Z"
}
```

| Field            | Required | Description                                   |
|------------------|----------|-----------------------------------------------|
| `bank`           | Yes      | Bank name (see supported banks below)         |
| `merchant_name`  | Yes      | Registered merchant name                      |
| `merchant_token` | Yes      | Merchant authentication token                 |
| `cc_number`      | Yes      | 16-digit card number                          |
| `card_type`      | Yes      | `debit`, `credit`, or `deposit`               |
| `cvv`            | Yes      | Card security code                            |
| `exp_date`       | Yes      | Expiration date (`MM/YY` or `MM/YYYY`)        |
| `amount`         | Yes      | Transaction amount as a string (`"25.00"`)    |
| `card_zip`       | No       | Billing ZIP for address verification          |
| `card_holder`    | No       | Cardholder name                               |
| `timestamp`      | No       | ISO 8601 timestamp                            |

### Responses

| Response                            | Meaning                                      |
|-------------------------------------|----------------------------------------------|
| `Approved.`                         | Transaction accepted by the bank             |
| `Declined - Insufficient Funds.`    | Account balance or credit limit too low      |
| `Declined - Credit Limit Exceeded.` | Over the card's credit line                  |
| `Declined - Daily Limit Exceeded.`  | Daily transaction cap hit                    |
| `Declined - Account Frozen.`        | Account is frozen                            |
| `Declined - Account Closed.`        | Account is closed                            |
| `Declined - Card Not Valid.`        | Card number not recognized                   |
| `Declined - Invalid Request.`       | Missing or malformed required fields         |
| `Merchant Not Authorized.`          | Merchant name/token failed authentication    |
| `Bank Not Supported.`               | Unknown bank name in request                 |

---

## Supported Banks

| Bank Name             | Auth Style         | Accepted Aliases                                     |
|-----------------------|--------------------|------------------------------------------------------|
| Jeff's Bank           | Body token         | `jeffs bank`, `jeff's bank`                         |
| Topher's Bank         | Body token         | `tophers bank`, `topher's bank`                     |
| Wild West Bank        | Body token         | `wild west bank`, `wild west`                       |
| CaliBear Credit Union | API key header     | `calibear`, `calibear bank`, `calibear credit union` |
| Corbin Bank           | Basic auth header  | `corbin bank`, `corbin`                             |
| Joseph's Bank         | Body token         | `josephs bank`, `joseph's bank`, `jank bank`        |

Each integration handles differences in field naming conventions, auth placement (body vs. headers), amount types (string vs. number), and transaction type enums.

---

## Running the Simulators

### Quick test — small batch
```bash
python3 merchant_simulator.py
```
Sends a variety of test transactions (good cards, bad CVVs, insufficient funds, etc.) and writes results to `transaction_log.txt`.

### Large-scale test — 500+ transactions
```bash
python3 merchant_simulator_500.py
```
Fires 510 randomized transactions across 5 banks and 50 real merchants. Prints live results and shows a per-bank breakdown when complete.

### Bulk endpoint tester
```bash
# from the csv/ directory (reads *_bank_accounts.csv and merchants.csv)
cd csv
python3 ../spam-cchs.py
```
Continuously cycles through all endpoints in `urls.txt`, sending one transaction per endpoint per pass. Logs everything to `bank_endpoint_log.txt`.

---

## Generating the Transaction Report

1. Export the `Transaction` DynamoDB table to CSV and name it `results.csv` inside `csv/`.
2. Run from the project root:
```bash
python3 build_report.py
```
Produces `transaction_report.xlsx` with three sheets:
- **Summary** — total transactions, largest/average amount, approval/decline rates
- **Merchants** — transaction count per merchant + pie chart
- **Banks** — transaction count per bank + pie chart

---

## CI/CD Pipeline

```
push to main
    └─► Deploy to Staging (GitHub Actions)
            └─► Run tests/staging_tests.py against /staging endpoint
                    ├─► All tests pass  →  Promote staging alias to production
                    └─► Any test fails  →  Block production deploy, exit 1
```

Staging and production are separate AWS Lambda **aliases** pointing to published versions of the same function. Production is only updated when the automated test suite passes.

---

## Database Design

Two DynamoDB tables back the system:

**Merchant** — stores registered merchants and their auth tokens  
**Transaction** — append-only log of every processed transaction

Full PK/SK layout and attribute schema: [DBDesign.md](DBDesign.md)

---

## Tech Stack

| Layer       | Technology                                   |
|-------------|----------------------------------------------|
| Runtime     | Python 3.11 on AWS Lambda                    |
| API         | AWS API Gateway (REST)                       |
| Database    | AWS DynamoDB                                 |
| HTTP client | `urllib3` (built into Lambda runtime)        |
| Reporting   | `openpyxl` (Excel report generation)         |
| CI/CD       | GitHub Actions                               |
| IaC         | AWS CLI (alias promotion via workflow)       |

---

## Security Notes

- Full card numbers are never stored — only the last 4 digits are written to the transaction log
- Merchant tokens are verified against DynamoDB on every request before any bank is contacted
- Bank credentials (tokens, API keys) live in Lambda environment config, not in source code
