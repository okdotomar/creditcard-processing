# Semester Project Requirements Document 

## Project Title: Banking Application
## Developer Name: Omar Rodriguez

### Business Context:

**Business Drivers and Goals.**

- We want to ensure our developers understans how to create a project from scratch. We want to teach competency for unexperienced developers in this field. We have several newly onboarded members and are working with them so they can become more skilled programmers and better leaders. 

**Description of the Domain.**
- The system is essentially going to be a credit card clearinghouse that will process credit card information and send it to be verified, process that information, send it to the bank, and approve or deny a transaction. Users will be making the purchases with a credit/debit card.

### Problem Statement
- We are creating a POS system level coding that validates credit/debit cards for banking institutions.

### Scope:
- We will include a clearinghouse that will process credit card information for MVP.
- Stretch goals will include some sort of wireless payment method

### Functional Requirements:
API that reads:
1. card holder name
2. bank name
3. credit or debit
4. expiration date
5. card zip code
6. transaction amount

7. needs to accept json data
8. call correct bank api
9. handle response from bank
10. handle errors
11. create and append to daily logs
12. write reports to make logs readable.
13. expected format for credit/debit cards should be 16 characters
14. manual card entry
15. PIN entry

### Non-Functional Requirements:
1. PCI DSS Compliance
2. Support EMV chip, NFC contactless payments
3. Batching and closing daily transactions
4. Connect to Wi-FI
5. Integration with multiple systems
6. Address Verification System
7. Subscription service for POS
8. POS system
9. Power outage handling
10. Fraud detection