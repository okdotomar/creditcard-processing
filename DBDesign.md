# Database Design (Credit Card Clearinghouse)

## Data Organization

I will separate tables to prevent any dependent tables and for sake of clarity and consistency. Separating these are more consistent with real world scenarios as these often act as separate entitites.

Tables:

1. Merchant
2. Bank
3. Transaction

# 1. Merchant Table

This will store merchant profiles and authentication information.

Partition Key: MerchantID(String)
Sort Key: None

Attributes:
- MerchantID (String, UUID)
- MerchantName (String)
- AuthToken (String, hashed)
- Status (String: Active/Inactive)

Reasoning:
- MerchantID is used instead of Merchant names to avoid any confusion, duplicates, or misspelling
- AuthToken is hashed for security
- MerchantName is not used because names can change

# 2. Bank Table

This will keep a unified list of valid banks. 

Partition Key: BankID (String)
Sort Key: None

Attributes:
- BankID (String, UUID)
- BankName (String)
- RoutingNumber (String)

Reasoning:
- BankID is used instead of Name to prevent inconsistency
- All Transactions will reference BankID
- Reduces data integrity issues.

# 3. Transaction Table

This stores all transaction records.

Partition Key: MerchantID
Sort Key: TransactionID

Attributes:
- TransactionID (String, UUID)
- MerchantID (String)
- Amount (String)
- BankID (String)
- Status (String)
- MaskedCardNumber (String)
- CreatedAt (String)

Reasoning:
- Using MerchantID as Partition allows for more efficient queries
- TransactionID ensures uniqueness
- Credit Cards are not in plain text

# PCI Compliance Considerations
- Full credit card numbers are never stored
- Only masked card numbers are used for logging
