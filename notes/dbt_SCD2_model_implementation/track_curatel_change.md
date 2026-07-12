# Track & Curate change

A well-designed **SCD Type 2 (SCD2)** implementation must strike a balance between two competing goals: **preserving a complete historical record of business changes** and **controlling storage growth and query performance**. The proposed implementation achieves this by recording only meaningful business changes while avoiding unnecessary duplicate records.

### Historical Completeness

The implementation guarantees historical completeness by creating a new version of a product whenever a tracked business attribute changes. Instead of overwriting existing data, the previous record is closed by setting `dbt_valid_to`, and a new record is inserted with a new surrogate key (`dbt_scd_id`), `dbt_valid_from`, and `dbt_valid_to = NULL`. This preserves every historical state of the product, enabling accurate point-in-time analysis.

For example:

| Date   | Product  | Price | Supplier   | Category    | Status |
| ------ | -------- | ----: | ---------- | ----------- | ------ |
| Jan 1  | Laptop A |  $999 | Supplier A | Electronics | Active |
| Feb 10 | Laptop A |  $949 | Supplier A | Electronics | Active |
| Apr 5  | Laptop A |  $949 | Supplier B | Electronics | Active |
| Jul 1  | Laptop A |  $949 | Supplier B | Computers   | Active |

Rather than updating a single row, SCD2 stores four historical versions. This enables analysts to answer questions such as:

* How did price reductions affect sales volume over time?
* Which supplier was responsible for the product during a specific sales period?
* When did the merchandising team reorganize categories?
* Which version of the product was active when a customer placed an order?

The design also handles more complex business scenarios:

* **Supplier relationship changes:** Every supplier transition creates a new historical version, allowing procurement teams to evaluate supplier performance and product quality over time.
* **Product reactivation:** If a product is discontinued and later reintroduced, SCD2 closes the discontinued record and creates a new active record rather than modifying the original. This preserves both historical periods and accurately reflects gaps in product availability.
* **Multiple simultaneous changes:** If price, supplier, and category all change in the same load, a single new version captures the complete new business state, maintaining consistency without generating unnecessary intermediate records.
* **Point-in-time reporting:** Because each version has validity dates, historical fact tables can be joined to the correct product version, ensuring reports reflect the attributes that were valid when each transaction occurred rather than today's values.

### Storage Efficiency

Although SCD2 intentionally stores multiple versions of a record, several strategies minimize unnecessary storage growth.

**1. Hash-based change detection**

Instead of comparing every tracked column individually, the staging model generates a `record_hash` using only business-critical attributes:

* Product name
* Category
* Price
* Supplier
* Product status

The snapshot uses:

```sql
strategy = 'check'
check_cols = ['record_hash']
```

This means a new historical record is created only when the combined business state changes. Changes to metadata, ingestion timestamps, or audit columns do not generate additional versions.

**2. Tracking only business-meaningful attributes**

Only attributes required for historical analysis are included in the hash. System-generated fields such as load timestamps are excluded because they change every execution and would otherwise create unnecessary historical records.

**3. Threshold-based change detection**

For organizations with frequent minor price fluctuations, storage can be further optimized by introducing business thresholds before generating a new version. Examples include:

* Record a new version only if the price changes by more than **5%**.
* Ignore temporary promotional price changes shorter than one day.
* Track supplier changes only after supplier contracts become effective.

These rules reduce storage while preserving changes that have meaningful analytical value.

**4. Surrogate key optimization**

Each historical version receives a unique surrogate key (`product_sk`), while the stable business key (`product_id`) identifies the product itself. This provides several benefits:

* Fact tables join using compact surrogate keys instead of repeatedly storing large business attributes.
* Historical joins remain accurate because each fact references the exact product version that was valid when the transaction occurred.
* Query performance improves through indexing or clustering on surrogate keys and validity dates.

**5. Separate current and historical models**

The snapshot maintains the complete historical dataset, while `dim_products_current` filters to records where `dbt_valid_to IS NULL`. Most operational dashboards query only the current dimension, reducing scan costs and improving performance, while historical analyses continue to use the snapshot when needed.

### Balancing Historical Completeness and Storage Efficiency

The implementation balances these objectives by ensuring that **every meaningful business event is preserved while preventing unnecessary version creation**.

For example, suppose a product experiences the following updates over one month:

* Daily ETL refreshes with no business changes
* One 8% price reduction
* One supplier change
* One category reorganization

Without optimization, daily loads could generate 30 historical versions. Using hash-based change detection, only the three meaningful business events produce new SCD2 records. If a threshold-based pricing rule is also applied, insignificant price fluctuations would be ignored, further reducing storage while retaining analytically valuable history.

As a result, the implementation provides:

* **Complete historical lineage** through versioned records with validity periods.
* **Accurate point-in-time reporting** by preserving every business state.
* **Efficient storage** by avoiding duplicate versions caused by system or metadata changes.
* **High query performance** through surrogate keys, separate current and historical models, and selective change detection.

This combination ensures that the SCD2 solution is both **historically comprehensive** and **production-ready**, supporting long-term analytics without incurring unnecessary storage or performance costs.
