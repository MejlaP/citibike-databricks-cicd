from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, round
import sys


# Read the single positional argument passed in via job.yml
catalog = sys.argv[1]

# Read from the Silver table using the dynamic catalog variable
df = spark.read.table(f"{catalog}.02_silver.jc_citibike")

# Second Gold aggregation — same daily grouping, but broken down per station too.
# Only avg duration and total trips are kept here (no min/max)
df = df.\
    groupBy("trip_start_date", "start_station_name").\
    agg(
    round(avg("trip_duration_mins"),2).alias("avg_trip_duration_mins"),
    count("ride_id").alias("total_trips")
    )

# Write the station-level daily aggregation as a managed Delta table in Gold
df.write.\
    mode("overwrite").\
    option("overwriteSchema", "true").\
    saveAsTable(f"{catalog}.03_gold.daily_station_performance")