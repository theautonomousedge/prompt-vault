# Data Model Blueprint — Prompt Vault

> Database schema and relationships. See `docs/api-reference.md` for field-level detail.

---

## Entity Relationship Diagram

```
┌──────────┐       ┌──────────┐       ┌──────────────┐
│   User   │──1:1──│ Profile  │       │  Connection  │
│          │       │          │       │  (UNUSED)    │
│  id (PK) │──1:1──│          │       │              │
│  email   │       │ city     │       │ giver_id(FK) │
│  type    │       │ state    │       │ recv_id (FK) │
│  pass    │       │ story    │       └──────────────┘
└────┬─────┘       │ verified │
     │              │ flagged  │
     │              └──────────┘
     │
     ├──1:1──┌──────────────┐
     │       │   Address    │
     │       │  (encrypted) │
     │       │              │
     │       │ enc_street   │
     │       │ enc_zip      │
     │       │ city, state  │
     │       └──────────────┘
     │
     └──1:N──┌──────────────┐
             │ Transaction  │
             │              │
             │ giver_id(FK) │
             │ recv_id (FK) │
             │ amount       │
             │ tip_amount   │
             │ delivery     │
             │ status       │
             │ stripe_id    │
             │ message      │
             └──────────────┘
```

## Relationships

| From | To | Type | Notes |
|------|----|------|-------|
| User → Profile | 1:1 | Only receivers/both have profiles |
| User → Address | 1:1 | Encrypted street + zip. City/state plaintext for filtering |
| User → Transaction (as giver) | 1:N | Donor's sent meals |
| User → Transaction (as receiver) | 1:N | Recipient's received meals |
| User → Connection | 1:N | **UNUSED** — deferred to Phase 5 |

## Enums

| Enum | Values | Used In |
|------|--------|---------|
| UserType | `giver`, `receiver`, `both`, `admin` | User.user_type |
| DeliveryMethod | `doordash`, `ubereats`, `instacart` | Transaction.delivery_method |
| TransactionStatus | `pending`, `completed`, `failed`, `refunded` | Transaction.status |

## Encryption Strategy

- **Encrypted fields**: `Address.encrypted_street`, `Address.encrypted_zip`
- **Algorithm**: Fernet (AES-128-CBC with HMAC-SHA256)
- **Key source**: `ENCRYPTION_KEY` env var
- **Fallback**: If no key set, generates temporary key (logged as warning). Data encrypted with temp key is lost on restart
- **Rule**: Encrypted data is NEVER returned in API responses to donors. Only used server-side for fulfillment
