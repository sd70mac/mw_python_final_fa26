create table if not exists public.orders (
    order_id uuid primary key,
    timestamp timestamptz not null,
    customer_name text not null,
    items jsonb not null
);

create index if not exists orders_timestamp_idx
    on public.orders (timestamp desc);

alter table public.orders enable row level security;
revoke all on table public.orders from anon, authenticated;
grant select, insert on table public.orders to service_role;
