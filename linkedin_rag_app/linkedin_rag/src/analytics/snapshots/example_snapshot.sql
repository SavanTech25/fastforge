
{% snapshot example_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

select * from {{ source('example_source', 'example_table') }}

{% endsnapshot %}
