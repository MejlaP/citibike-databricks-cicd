from pyspark.sql.functions import unix_timestamp, col

def get_trip_duration_mins(df, start_col, end_col, output_col):
    """
    Adds a column to the DataFrame calculating the difference in minutes between two timestamp columns.
    Parameters:
      df: Spark DataFrame.
      start_col (str): Name of the column with the start timestamp.
      end_col (str): Name of the column with the end timestamp.
      output_col (str): Name of the resulting column.
    Returns:
      DataFrame with an additional column showing the difference in minutes.
    """
    return df.withColumn(
        output_col,
        # unix_timestamp converts each timestamp to seconds since epoch,
        # so subtracting gives duration in seconds; dividing by 60 converts to minutes
        (unix_timestamp(col(end_col)) - unix_timestamp(col(start_col))) / 60
    )