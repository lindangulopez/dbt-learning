{% snapshot customer_snapshot %}

{{
    config(

        target_schema='public',

        unique_key='customer_id',

        strategy='check',

        check_cols=[
            'customer_name',
            'email_address',
            'shipping_address',
            'customer_segment'
        ],

        invalidate_hard_deletes=True

    )
}}

SELECT
    customer_id,
    customer_name,
    email_address,
    shipping_address,
    customer_segment,
    load_date

FROM from {{ ref('stg_customers') }}

{% endsnapshot %}
