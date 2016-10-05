To perform the search, I first find bounding min and max latitude and longitudes to narrow down the search. Having a dictionary of shop_ids keyed on latitude
and also on latitude, it is efficient to filter shop_ids by lattitude and
longitude. Unfortunately, given that the shops are all relatively close to each other, this doesn't narrow down the search as much as I had hoped.

A better method, I think, would be to use a kd-tree to organise the positional
coordinates of the shop locations, and use this to find all shops within a
given distance of the search location. Initially I decided not to do this,
since lat/long are not linear with distance. However, after reading a response
on
http://stackoverflow.com/questions/20654918/python-how-to-speed-up-calculation-of-distances-between-cities
I see that it would be quite trivial to first convert lat, long coordinates to three dimensional ECEF coordinates and then create a kd-tree based on these.
scipy.spatial.KDTree has a useful query_ball_point method which could be used
to find all shops within the search range. In this case it would not be
necessary to construct SHOPS_BY_LAT and SHOPS_BY_LNG, but instead an array of tuples of the form (shop_lat, shop_lng, shop_id), along with SHOPS_BY_ID and
SHOPS_BY_TAG.



1. How would your design change if the data was not static (i.e updated frequently
during the day)?

2. Do you think your design can handle 1000 concurrent requests per second? If not, what
would you change?
