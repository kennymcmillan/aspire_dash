# Design board: Fencing Reports, October 2026

Prototype pages from the 2026-10-19 design pass (A/B/C directions, desktop + 390px phone, real public data).
Open any file in a browser. Only pages built from public data live here; athlete pages stay private.

| Page | Directions | Picked |
|---|---|---|
| competitions_list.html | A month-grouped table, B card grid, C season strip + agenda | A |
| filters_loading_icons.html | filter bar A/B/C, skeleton vs spinner vs top bar, weapon/category/level/source icons | A + skeleton |
| region_tile_maps.html | Gulf + Asia team ranks: A choropleth + bubbles, B hex tiles, C tile map linked to a ranked list | C |

Library follow-ups from this board: `sports.data_table(fit="content")` (Tidy fit, v0.110), the Plotly template
refresh in `charts.py`, and a reusable `region_tile_map` candidate (option C) for any sport's nation ranks.
