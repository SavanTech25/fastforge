with source as (
    select * from {{ ref('int_linkedin_posts') }}
)

select 
    author,
    count(*) as post_count,
    avg(char_count) as avg_char_count
from source
group by 1