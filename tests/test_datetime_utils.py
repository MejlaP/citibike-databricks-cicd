# test_datetime_utils.py
import datetime
from utils.datetime_utils import timestamp_to_date_col


def test_timestamp_to_date_col(spark):

    # Single row with one known timestamp — we just need to verify the date
    # part gets extracted correctly
    data = [(datetime.datetime(2025, 4, 10, 10, 30, 0),)]
    schema = "ride_timestamp timestamp"
    df = spark.createDataFrame(data, schema=schema)

    result_df = timestamp_to_date_col(df, "ride_timestamp", "ride_date")

    # first() gets just the first row — fine here since we only have one row
    row = result_df.select("ride_date").first()
    expected_date = datetime.date(2025, 1, 1)  # TEMPORARY: deliberately wrong to test AI summary
    assert row["ride_date"] == expected_date