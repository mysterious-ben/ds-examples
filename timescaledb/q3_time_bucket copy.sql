SELECT 
    time_bucket('5 minutes', apparent_time) + '5 minutes' AS five_min, 
    avg(measurement) 
FROM sensors_series
WHERE source = 'temperature'
GROUP BY five_min;
