from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, current_timestamp, arrays_zip

# -----------------------------------
# 1. Create Spark Session
# -----------------------------------
spark = SparkSession.builder \
    .appName("lecture11-weather-etl") \
    .getOrCreate()

# -----------------------------------
# 2. Robust Paths (FIXED)
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

input_path = str(BASE_DIR / "assignment_b_submission/lecture11b-open-meteo-raw.json")

current_output = str(BASE_DIR / "assignment_b_submission/curated_current_weather")
daily_output = str(BASE_DIR / "assignment_b_submission/curated_daily_weather")

# -----------------------------------
# 3. Read JSON
# -----------------------------------
df = spark.read.option("multiline", "true").json(input_path)

print("📥 Raw Schema:")
df.printSchema()

# -----------------------------------
# 4. Transform CURRENT weather
# -----------------------------------
current_df = df.select(
    col("latitude"),
    col("longitude"),
    col("timezone"),
    col("current.time").alias("timestamp"),
    col("current.temperature_2m").alias("temperature_c"),
    col("current.relative_humidity_2m").alias("humidity"),
    col("current.wind_speed_10m").alias("wind_speed"),
    col("current.weather_code").alias("weather_code")
).withColumn("processed_at", current_timestamp())

# -----------------------------------
# 5. Transform DAILY weather (FIXED)
# -----------------------------------
# Zip arrays together → avoid incorrect cross join
daily_zipped = df.select(
    col("latitude"),
    col("longitude"),
    col("timezone"),
    arrays_zip(
        col("daily.time"),
        col("daily.temperature_2m_max"),
        col("daily.temperature_2m_min"),
        col("daily.precipitation_sum")
    ).alias("daily_data")
)

daily_df = daily_zipped.select(
    col("latitude"),
    col("longitude"),
    col("timezone"),
    explode(col("daily_data")).alias("daily_row")
).select(
    col("latitude"),
    col("longitude"),
    col("timezone"),
    col("daily_row.time").alias("date"),
    col("daily_row.temperature_2m_max").alias("temp_max"),
    col("daily_row.temperature_2m_min").alias("temp_min"),
    col("daily_row.precipitation_sum").alias("precipitation")
).withColumn("processed_at", current_timestamp())

# -----------------------------------
# 6. Write outputs
# -----------------------------------
current_df.write.mode("overwrite").parquet(current_output)
daily_df.write.mode("overwrite").parquet(daily_output)

print("✅ ETL SUCCESS")
print(f"📦 Current weather → {current_output}")
print(f"📦 Daily weather → {daily_output}")

# -----------------------------------
# 7. Stop Spark
# -----------------------------------
spark.stop()