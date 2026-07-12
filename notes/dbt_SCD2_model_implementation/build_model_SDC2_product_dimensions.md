# **production-ready dbt SCD Type 2 implementation** 

* follows dbt best practices for an ecommerce **Product Dimension**.

Project Structure

```text
models/
   staging/
      stg_products.sql
      schema.yml

   marts/
      dimensions/
          dim_products_current.sql
          schema.yml

snapshots/
      products_snapshot.sql

tests/
      single_current_record.sql
      temporal_validity.sql
```

---

# Step 1 — Staging Model

`models/staging/stg_products.sql`

```sql
{{ config(materialized='view') }}

with source as (

    select *
    from {{ source('raw', 'products') }}

),

cleaned as (

    select

        cast(product_id as varchar)      as product_id,
        trim(product_name)               as product_name,
        trim(category)                   as category,
        cast(price as numeric(12,2))     as price,
        trim(supplier)                   as supplier,
        upper(status)                    as product_status,

        current_timestamp                as snapshot_loaded_at,

        {{ dbt_utils.generate_surrogate_key([
            'product_name',
            'category',
            'price',
            'supplier',
            'product_status'
        ]) }} as record_hash

    from source

)

select *
from cleaned
```

## Why this design?

Business Key

```
product_id
```

Tracked Attributes

* product_name
* category
* price
* supplier
* status

Metadata

* snapshot_loaded_at
* record_hash

The hash dramatically speeds up change detection compared to comparing every field.


## Step 2 — Snapshot Configuration

`snapshots/products_snapshot.sql`

```sql
{% snapshot products_snapshot %}

{{
    config(

        target_schema='snapshots',

        unique_key='product_id',

        strategy='check',

        check_cols=[
            'record_hash'
        ],

        invalidate_hard_deletes=True

    )
}}

select *

from {{ ref('stg_products') }}

{% endsnapshot %}
```

---

### Why Check Strategy?

Product data usually lacks a trustworthy "last_updated" timestamp.

Instead we compare

```
record_hash
```

which includes

* name
* category
* price
* supplier
* status

This means:

Price changed?

→ New historical record

Supplier changed?

→ New historical record

Category changed?

→ New historical record

Only non-business metadata changes?

→ Ignore

---

## Step 3 — Current Dimension Model

`models/marts/dimensions/dim_products_current.sql`

```sql
{{ config(materialized='table') }}

select

    dbt_scd_id             as product_sk,

    product_id,

    product_name,

    category,

    price,

    supplier,

    product_status,

    dbt_valid_from         as effective_date,

    dbt_valid_to           as expiry_date,

    datediff(
        day,
        dbt_valid_from,
        current_timestamp
    ) as days_since_last_change

from {{ ref('products_snapshot') }}

where dbt_valid_to is null
```

---

Current dimension contains only active products.

Example

| product_sk | product_id | price  | supplier |
| ---------- | ---------- | ------ | -------- |
| A89...     | P1001      | 120.00 | ABC Ltd  |

Fact tables should join using

```
product_sk
```

NOT

```
product_id
```

because facts must preserve historical context.

---

## Optional Historical Dimension

Many production projects also create

```sql
dim_products_history.sql
```

```sql
{{ config(materialized='table') }}

select

    dbt_scd_id as product_sk,

    product_id,

    product_name,

    category,

    supplier,

    price,

    product_status,

    dbt_valid_from,

    dbt_valid_to

from {{ ref('products_snapshot') }}
```

This powers historical reporting.

---

## Step 4 — Data Quality Tests

### models/marts/dimensions/schema.yml

```yaml
version: 2

models:

  - name: dim_products_current

    columns:

      - name: product_sk
        tests:
          - unique
          - not_null

      - name: product_id
        tests:
          - not_null

      - name: price
        tests:
          - not_null

      - name: supplier
        tests:
          - not_null
```

---

### Snapshot Tests

```yaml
version: 2

snapshots:

  - name: products_snapshot

    columns:

      - name: product_id
        tests:
          - not_null

      - name: dbt_scd_id
        tests:
          - unique
```

---

### Custom Test 1

Exactly One Current Record

`tests/single_current_record.sql`

```sql
select

product_id

from {{ ref('products_snapshot') }}

where dbt_valid_to is null

group by product_id

having count(*) > 1
```

Expected result

```
0 rows
```

---

### Custom Test 2

Temporal Validity

`tests/temporal_validity.sql`

```sql
select *

from {{ ref('products_snapshot') }}

where

dbt_valid_to is not null

and dbt_valid_from >= dbt_valid_to
```

Should return

```
0 rows
```

---

### Custom Test 3

Negative Prices

`tests/valid_price.sql`

```sql
select *

from {{ ref('products_snapshot') }}

where

price < 0

or price > 100000
```

---

### Custom Test 4

Business Key Completeness

```yaml
columns:

  - name: product_id
    tests:
      - unique
      - not_null
```

---

## Example History

Initial Load

| product_id | price | supplier |
| ---------- | ----- | -------- |
| 101        | 100   | ABC      |

Snapshot

| product | price | valid_from | valid_to |
| ------- | ----- | ---------- | -------- |
| 101     | 100   | Jan 1      | NULL     |

---

Price Changes

```
100

↓

115
```

Snapshot

| product | price | valid_from | valid_to |
| ------- | ----- | ---------- | -------- |
| 101     | 100   | Jan1       | Jan15    |
| 101     | 115   | Jan15      | NULL     |

---

Supplier Changes

```
ABC

↓

XYZ
```

Snapshot

| product | supplier | valid_from | valid_to |
| ------- | -------- | ---------- | -------- |
| 101     | ABC      | Jan15      | Feb2     |
| 101     | XYZ      | Feb2       | NULL     |

Entire history is preserved automatically.

---

## Production Performance Optimizations

* Use a `record_hash` (`dbt_utils.generate_surrogate_key`) to minimize comparison overhead during snapshots.
* Materialize the current dimension as a table for fast analyst queries.
* Add indexes or clustering on `product_id`, `dbt_valid_to`, and `dbt_valid_from` where your warehouse supports them.
* Partition or cluster large snapshot tables by `dbt_valid_from` (or date) for efficient historical queries.
* Enable `invalidate_hard_deletes: true` to properly close records when products are removed from the source.
* Join fact tables using `product_sk` (`dbt_scd_id`) to preserve historical accuracy.

---

## Typical dbt Execution Order

```bash
dbt run --select stg_products

dbt snapshot

dbt run --select dim_products_current

dbt test
```

This implementation provides a production-ready SCD Type 2 solution with efficient hash-based change detection, automatic historical versioning, an analyst-friendly current dimension, and comprehensive data quality tests to ensure historical integrity and query performance.
