import sys


from citibike.citibike_utils import get_trip_duration_mins
from utils.datetime_utils import timestamp_to_date_col
from pyspark.sql.functions import create_map, lit


# Read positional command-line arguments passed in via the job's "parameters" list
pipeline_id = sys.argv[1]
run_id = sys.argv[2]
task_id = sys.argv[3]
processed_timestamp = sys.argv[4]
catalog = sys.argv[5]

# Read from the Bronze table using the dynamic catalog variable
df = spark.read.table(f"{catalog}.01_bronze.jc_citibike")

# Compute trip duration in minutes
df = get_trip_duration_mins(df, "started_at", "ended_at", "trip_duration_mins")

# Derive trip_start_date from started_at, needed for daily aggregations in Gold
df = timestamp_to_date_col(df, "started_at", "trip_start_date")

# Add metadata map column using real job/run identifiers passed in as script arguments
df = df.withColumn("metadata", 
              create_map(
                  lit("pipeline_id"), lit(pipeline_id),
                  lit("run_id"), lit(run_id),
                  lit("task_id"), lit(task_id),
                  lit("processed_date"), lit(processed_timestamp)
                  ))

# Keep only the columns relevant for the Silver layer
df = df.select(
    "ride_id",
    "trip_start_date",
    "started_at",
    "ended_at",
    "start_station_name",
    "end_station_name",
    "trip_duration_mins",
    "metadata"
    )

# Write the Silver-layer DataFrame as a managed Delta table
df.write.\
    mode("overwrite").\
    option("overwriteSchema", "true").\
    saveAsTable(f"{catalog}.02_silver.jc_citibike")