with source as (
    select * from {{ ref('raw_linkedin_posts') }}
)

select 
    id,
    lower(text) as text,
    author,
    created_at,
    length(text) as char_count
from source