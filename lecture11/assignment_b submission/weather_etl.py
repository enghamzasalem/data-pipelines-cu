from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("weather-etl").getOrCreate()

df = spark.read.json("data/raw_weather.json")

print("=== RAW DATA ===")
df.show(truncate=False)

print("=== SCHEMA ===")
df.printSchema()


clean = df.selectExpr(
    "latitude",
    "longitude",
    "current.temperature_2m as temperature_2m"
)

print("=== CLEAN DATA ===")
clean.show()

clean.write.mode("overwrite").parquet("output/weather_curated")

spark.stop()