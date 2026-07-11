select

    customer_id,
    customer_name,
    email_address,
    shipping_address,
    customer_segment

from {{ ref('customer_snapshot') }}

where dbt_valid_to is null
