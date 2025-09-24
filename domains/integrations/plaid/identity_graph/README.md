# Plaid Identity Graph

**Status:** Parked / Future Feature

This directory is reserved for the `Plaid Identity Graph` service, which was originally developed in the `_parked/` directory. The code was lost during a git history rewrite, but the architectural intent is preserved here.

## Purpose

The Identity Graph service was designed to link and resolve identities across different financial platforms (QBO, Plaid, etc.) to create a unified view of vendors and customers. This is critical for:

-   **Deduplication:** Preventing duplicate vendor/customer records when syncing from multiple sources.
-   **Enrichment:** Combining data from Plaid (e.g., real bank transaction names) with data from QBO (e.g., vendor records) to get a more complete picture.
-   **Advanced Analytics:** Understanding the true identity of payees and payers for more accurate cash flow analysis.

## Future Implementation

When this feature is prioritized, the service should be re-implemented here with the following considerations:
-   Fuzzy matching algorithms for names.
-   Rules-based entity resolution.
-   Integration with the `Vendor` and `Customer` domain models.
