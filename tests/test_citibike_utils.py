# test_citibike_utils.py
import datetime
from citibike.citibike_utils import get_trip_duration_mins


# "spark" here is the fixture we defined in conftest.py — pytest automatically
# injects it because the parameter name matches the fixture name
def test_get_trip_duration_mins(spark):

    # Create a small test DataFrame with known start/end timestamps,
    # so we know exactly what the expected duration should be
    data = [
        (datetime.datetime(2025, 4, 10, 10, 0, 0), datetime.datetime(2025, 4, 10, 10, 10, 0)),  # 10 minutes
        (datetime.datetime(2025, 4, 10, 10, 0, 0), datetime.datetime(2025, 4, 10, 10, 30, 0))   # 30 minutes
    ]
    schema = "start_timestamp timestamp, end_timestamp timestamp"
    df = spark.createDataFrame(data, schema=schema)

    # Call the actual helper function used in the Silver notebooks/scripts —
    result_df = get_trip_duration_mins(df, "start_timestamp", "end_timestamp", "trip_duration_mins")

    # collect() pulls the results back from Spark into a plain Python list,
    # so we can assert on the actual values
    results = result_df.select("trip_duration_mins").collect()

    # Verify the calculated durations match what we expect (10 and 30 minutes)
    assert results[0]["trip_duration_mins"] == 10
    assert results[1]["trip_duration_mins"] == 30