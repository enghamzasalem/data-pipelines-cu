from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("weather-etl").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

data = [{
    "latitude": 48.8566,
    "longitude": 2.3522,
    "city": "Paris",
    "temperature_2m": 12.3,
    "temperature_2m_max": 14.1,
    "temperature_2m_min": 7.8,
    "precipitation_sum": 0.1,
    "wind_speed_10m": 14.2,
    "observation_date": "2024-01-15"
}]

df = spark.createDataFrame(data)
print("=== Raw weather data ===")
df.show()

clean = df.select(
    "city",
    "observation_date",
    "temperature_2m",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum"
)

print("=== Curated output ===")
clean.show()

clean.write.mode("overwrite").parquet("out/weather_curated")
print("✅ Written to out/weather_curated")
spark.stop()
