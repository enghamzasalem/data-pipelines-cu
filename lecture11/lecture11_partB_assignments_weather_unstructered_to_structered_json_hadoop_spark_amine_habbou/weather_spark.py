from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
import requests
import json
import os
from datetime import datetime
import os

output_dir = "/home/vagrant/spark_weather_project"
os.makedirs(output_dir, exist_ok=True)

local_path = os.path.join(output_dir, "output.json")
# =====================
# SPARK SESSION
# =====================
spark = SparkSession.builder \
    .appName("WeatherSparkPipeline") \
    .getOrCreate()

# =====================
# FETCH API
# =====================
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 53.08,
    "longitude": 8.80,
    "current_weather": True
}

raw = requests.get(url, params=params).json()

# =====================
# LOAD INTO SPARK
# =====================
df = spark.read.json(
    spark.sparkContext.parallelize([raw])
)

# =====================
# TRANSFORM (STRUCTURING STEP)
# =====================
df_clean = df.select(
    col("latitude"),
    col("longitude"),
    col("current_weather.temperature").alias("temperature_c"),
    col("current_weather.windspeed").alias("windspeed_kmh"),
    col("current_weather.weathercode").alias("weather_code")
)

df_clean = df_clean.withColumn(
    "conditions_short",
    when(col("weather_code") == 0, "clear sky")
    .when(col("weather_code") <= 2, "partly cloudy")
    .otherwise("unknown")
)

# =====================
# OUTPUT PATHS
# =====================

# HDFS (for Hadoop requirement)
hdfs_path = "hdfs://master:9000/user/vagrant/weather_structured"

# LOCAL (for WSL copy)
local_path = "/home/vagrant/spark_weather_project/output.json"

# =====================
# SAVE TO HDFS
# =====================
df_clean.write.mode("overwrite").json(hdfs_path)

# =====================
# SAVE LOCAL JSON (for your WSL)
# =====================
data = df_clean.collect()
result = [row.asDict() for row in data]

with open(local_path, "w") as f:
    json.dump(result, f, indent=2)

print("DONE")
print("HDFS:", hdfs_path)
print("LOCAL FILE:", local_path)

spark.stop()
