with source as (
    select * from raw_linkedin_posts
)

select 
    id,
    text,
    author,
    created_at::timestamp as created_at
from source