from pyspark.sql.types import StructType, StructField, StringType, DecimalType, TimestampType
from pyspark.sql.functions import create_map, lit
import sys


# Read positional command-line arguments passed in via the job's "parameters" list
# (order must exactly match the order defined in job.yml)
pipeline_id = sys.argv[1]
run_id = sys.argv[2]
task_id = sys.argv[3]
processed_timestamp = sys.argv[4]
catalog = sys.argv[5]

# Explicitly define the schema for the Bronze layer, converting raw string fields
# from Landing into proper timestamp and decimal types
schema = StructType([
    StructField("ride_id", StringType(), True),
    StructField("rideable_type", StringType(), True),
    StructField("started_at", TimestampType(), True),
    StructField("ended_at", TimestampType(), True),
    StructField("start_station_name", StringType(), True), 
    StructField("start_station_id", StringType(), True),   
    StructField("end_station_name", StringType(), True), 
    StructField("end_station_id", StringType(), True), 
    StructField("start_lat", DecimalType(), True), 
    StructField("start_lng", DecimalType(), True), 
    StructField("end_lat", DecimalType(), True), 
    StructField("end_lng", DecimalType(), True), 
    StructField("member_casual", StringType(), True), 
])

# Read raw CSV from the Landing volume using the dynamic catalog variable,
# applying the explicit schema instead of relying on automatic inference
df = spark.read.csv(f"/Volumes/{catalog}/00_landing/source_citibike_data/JC-202503-citibike-tripdata.csv", schema=schema, header=True)

# Add metadata column for pipeline lineage/observability, using real job/run
# identifiers passed in as script arguments
df = df.withColumn("metadata", 
              create_map(
                  lit("pipeline_id"), lit(pipeline_id),
                  lit("run_id"), lit(run_id),
                  lit("task_id"), lit(task_id),
                  lit("processed_date"), lit(processed_timestamp)
                  ))

# Write the transformed DataFrame as a managed Delta table in the Bronze schema
df.write.\
    mode("overwrite").\
    option("overwriteSchema", "true").\
    saveAsTable(f"{catalog}.01_bronze.jc_citibike")