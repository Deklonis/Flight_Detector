create table if not exists api_get (
    id bigserial primary key,
    api_time timestamptz not null,
    create_at timestamptz default now()
);

create table if not exists aircraft (
    icao24 varchar(6) primary key,
    origin_country varchar(60)
);


create table if not exists squawk_status (
    id bigserial primary key,
    squawk_name varchar(4),
    sq_status varchar(40)
);

create table if not exists aircraft_states (
    id bigserial primary key,
    api_id bigint references api_get(id) on delete cascade,
    icao24 varchar(6) references aircraft(icao24) on delete set null,
    callsign varchar(20),

    time_position timestamptz,
    last_contact timestamptz,

    longitude float,
    latitude float,

    geo_altitude float,
    velocity decimal(6, 2),
    true_track float,
    vertical_rate int,

    squawk varchar(4), --сейчас squawk_id

    on_ground boolean
);

alter table aircraft_states drop column if exists squawk;
alter table aircraft_states add column if not exists squawk_id bigint references squawk_status(id) on delete set null;
alter table aircraft alter column origin_country type varchar(60);

create unique index if not exists squawk_status_uniq_index on squawk_status (squawk_name);
create index if not exists aircraft_states_api_id_idx on aircraft_states (api_id);
create index if not exists aircraft_states_icao24_idx on aircraft_states (icao24);
create index if not exists aircraft_states_longitude_index on aircraft_states (longitude);
create index if not exists aircraft_states_latitude_index on aircraft_states (latitude);

insert into squawk_status (squawk_name, sq_status) values
    ('7500', 'Захват воздушного судна'),
    ('7600', 'Отказ радиосвязи'),
    ('7700', 'Аварийная ситуация')
on conflict (squawk_name) do nothing;