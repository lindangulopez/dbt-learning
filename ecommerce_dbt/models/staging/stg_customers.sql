select

    customer_id,
    customer_name,
    email_address,
    shipping_address,
    customer_segment,
    load_date,

    md5(
        concat(
            customer_name,
            email_address,
            shipping_address,
            customer_segment
        )
    ) as record_hash

from {{ source('ecommerce', 'staging_customer') }}
