## Schema
Table places (OpenStreetMap-style points of interest in Agartala). Columns: id integer, name text, category text, geom geometry(Point, 4326) in longitude/latitude.

## Categories
The category column only has these values: hospital, school, park, restaurant. Always use lowercase singular values like category = 'hospital'.

## Output rules
Always select name, category and ST_AsText(geom) AS wkt for list questions so results can be drawn on a map. For counting questions use COUNT(*). Return one SELECT statement only.

## Distance rule
To find places within a distance use ST_DWithin on geography so the distance is in metres: ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography, metres). Agartala city centre is lon 91.2868, lat 23.8315.

## Nearest rule
To find the nearest places order by distance: ORDER BY geom::geography <-> ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography LIMIT n.

## Example 1
Q: List all hospitals
SQL: SELECT name, category, ST_AsText(geom) AS wkt FROM places WHERE category = 'hospital'

## Example 2
Q: How many schools are there?
SQL: SELECT COUNT(*) AS total FROM places WHERE category = 'school'

## Example 3
Q: Restaurants within 1 km of the city centre
SQL: SELECT name, category, ST_AsText(geom) AS wkt FROM places WHERE category = 'restaurant' AND ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(91.2868, 23.8315), 4326)::geography, 1000)

## Example 4
Q: Nearest park to the city centre
SQL: SELECT name, category, ST_AsText(geom) AS wkt FROM places WHERE category = 'park' ORDER BY geom::geography <-> ST_SetSRID(ST_MakePoint(91.2868, 23.8315), 4326)::geography LIMIT 1
