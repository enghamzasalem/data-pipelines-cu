from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("weather-etl").getOrCreate()

df = spark.read.json("raw_weather.json")

print("Original schema:")
df.printSchema()

print("Original data:")
df.show(truncate=False)

clean = df.select(
    "latitude",
    "longitude",
    "timezone",
    "elevation",
    "current_weather.time",
    "current_weather.temperature",
    "current_weather.windspeed",
    "current_weather.winddirection",
    "current_weather.weathercode"
)

print("Curated weather data:")
clean.show(truncate=False)

clean.write.mode("overwrite").parquet("output_weather")

spark.stop()