from pyspark.sql.functions import max, min, avg, count, round
import sys


# Read the single positional argument passed in via job.yml — this task only
# needs "catalog" (unlike Bronze/Silver, no pipeline_id/run_id/task_id metadata here)
catalog = sys.argv[1]

# Read from the Silver table using the dynamic catalog variable
df = spark.read.table(f"{catalog}.02_silver.jc_citibike")

# Aggregate into daily summary statistics — one row per trip_start_date.
# round(..., 2) keeps duration metrics to 2 decimal places for cleaner reporting
df = df.groupBy("trip_start_date").agg(
    round(max("trip_duration_mins"),2).alias("max_trip_duration_mins"),
    round(min("trip_duration_mins"),2).alias("min_trip_duration_mins"),
    round(avg("trip_duration_mins"),2).alias("avg_trip_duration_mins"),
    count("ride_id").alias("total_trips")
)

# Write the first Gold-layer aggregation as a managed Delta table
df.write.\
    mode("overwrite").\
    option("overwriteSchema", "true").\
    saveAsTable(f"{catalog}.03_gold.daily_ride_summary")