create view plane_on_ground as
	select
		icao24,
		callsign,
		time_position
	from
		aircraft_states
	where
		on_ground = true
	and
		api_id = (
			select
				id
			from
				api_get
			where
				api_time = (select max(api_time) from api_get))

create view emergency_situation as 
select
	a.icao24,
	s.squawk_name,
	s.sq_status,
	a.last_contact,
	ap.api_time
from
	aircraft_states a
join
	squawk_status s
on
	s.id = a.squawk_id
join
	api_get ap
on
	ap.id = a.api_id
where
	s.squawk_name in ('7700', '7600', '7500')
order by ap.api_time desc
