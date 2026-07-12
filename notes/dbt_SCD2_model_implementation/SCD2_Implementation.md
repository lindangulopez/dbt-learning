# Summary of Lesson Notes

## SCD2 Implementation: Balancing Historical Completeness and Storage Efficiency

A well-designed SCD2 implementation preserves complete historical records while controlling storage growth by tracking only meaningful business changes.

Key principles:

* Track only **business-critical attributes** that provide analytical value, such as:

  * Product price changes
  * Supplier relationships
  * Category changes
  * Product status updates

* Use **hash-based change detection (`record_hash`)** to efficiently identify changes and avoid creating unnecessary historical versions.

* Maintain complete historical tracking through dbt-generated fields:

  * `dbt_valid_from` → records when a version became active.
  * `dbt_valid_to` → records when a version was replaced (`NULL` indicates the current record).
  * `dbt_scd_id` → provides a unique surrogate key for each historical version.

* Improve storage efficiency through:

  * Selective attribute tracking
  * Surrogate key optimization
  * Separate current and historical dimension models
  * Threshold-based change detection when frequent minor changes occur (for example, ignoring insignificant price fluctuations)

---

## dbt Snapshot Configuration and Change Detection

The **`check` strategy with `check_cols`** provides the most granular control over which changes create new SCD2 records.

Example:

```sql
check_cols = [
    'product_name',
    'category',
    'price',
    'supplier_id'
]
```

This approach allows the developer to define exactly which business attributes should be monitored.

Benefits:

* Prevents unnecessary historical records from non-business changes.
* Ensures important business events are captured.
* Provides better control over storage growth and historical accuracy.

A new historical record is created when **any one of the specified fields changes**.

Example:

* Price changes → New SCD2 record created.
* Supplier changes → New SCD2 record created.
* Category changes → New SCD2 record created.
* No tracked fields change → No new record created.

---

## Executing dbt Snapshots

The command used to execute dbt snapshots and process SCD2 changes is:

```bash
dbt snapshot
```

This command:

* Runs snapshot models.
* Compares current source data against previous snapshots.
* Detects changes using the configured strategy.
* Expires old records by updating `dbt_valid_to`.
* Creates new historical versions with updated validity dates and surrogate keys.

---

## Employee SCD2 Tracking Best Practice

For employee history tracking, use the **check strategy with business-critical fields** rather than tracking every column.

Recommended tracked attributes:

* Department
* Salary
* Job title
* Manager assignments

This approach captures valuable organizational changes while avoiding unnecessary records caused by system-generated fields such as:

* Last login timestamps
* Audit fields
* Technical metadata

It provides a balance between:

* Historical accuracy
* Storage efficiency
* Query performance

---

# Document Management and Accounting Data Quality Notes

## Professional Accounting Document Naming Conventions

Effective document naming standards should include:

* **Entity identification codes or abbreviations**

  * Identify the company, client, or business unit associated with the document.

* **Document type classifications using standard abbreviations**

  * Examples:

    * INV = Invoice
    * PO = Purchase Order
    * JE = Journal Entry

* **Unique reference numbers**

  * Prevent confusion between similar documents and improve traceability.

Individual team member initials should generally not be part of naming conventions because they create inconsistency and are dependent on staff changes.

---

## Document Log Verification and Cross-System Validation

Comprehensive document verification should include:

### Sequential gap identification

Used to detect missing documents in numbering sequences.

The most effective technique is:

✅ **Comparing differences between consecutive document numbers**

Example:

| Invoice  | Difference |
| -------- | ---------: |
| INV-1001 |          - |
| INV-1002 |          1 |
| INV-1003 |          1 |
| INV-1005 |          2 |

The gap indicates a missing invoice (`INV-1004`).

Common methods:

* Excel formulas calculating differences between consecutive numbers.
* SQL `LAG()` or `LEAD()` functions.
* Automated audit scripts.

---

### Cross-System Validation

Matching accounting system transaction logs with document storage inventories provides the highest value because it identifies whether financial transactions have supporting documentation.

It detects:

* Missing invoices or receipts
* Transactions without attachments
* Documents stored without accounting links
* Duplicate or mismatched records

Example:

QuickBooks transactions:

```
189 transactions
```

Document storage:

```
185 files
```

Duplicate files:

```
3 duplicates
```

Unique documents:

```
185 - 3 = 182
```

Net discrepancy:

```
189 - 182 = 7 missing documents
```

---

## Metadata Management Best Practices

### Relationship Metadata

Relationship metadata enables rapid document retrieval by connecting documents to business entities.

Examples:

* Invoice → Supplier
* Contract → Business unit
* Receipt → Accounting transaction
* Purchase order → Vendor

This allows users to search documents based on business relationships rather than only file names.

---

## Metadata System Consistency

The strongest approach for maintaining metadata consistency across teams is:

✅ **Template-based creation with standardized validation rules**

Benefits:

* Consistent metadata structures
* Reduced human errors
* Required fields enforced
* Easier auditing and reporting
* Scalable processes as teams grow

Avoid:

* Individual customization based on personal preference.
* Excessive client-specific variations.
* Manual-only review processes.

---

## Metadata Quality Control

The most effective way to prevent metadata degradation in growing accounting practices is:

✅ **Pattern-based monitoring that identifies systematic inconsistencies**

Benefits:

* Detects recurring metadata errors.
* Finds inconsistent naming patterns.
* Identifies missing required fields.
* Provides proactive quality control.

Compared with annual reviews or individual performance tracking, pattern-based monitoring is more scalable and identifies system-level issues earlier.
