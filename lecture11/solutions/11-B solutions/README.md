
# 📌 Lecture 11-B – Spark Weather ETL Pipeline

## 🔹 What I did

* Set up a Spark environment on a Vagrant-based Ubuntu VM
* Fetched weather data from the Open-Meteo API in JSON format
* Implemented a PySpark ETL pipeline (`weather_etl.py`)
* Loaded raw JSON data into a Spark DataFrame
* Selected and transformed relevant weather features (e.g., temperature, windspeed)
* Stored the processed data in Parquet format

---

## 🔹 Issue encountered

* Initial SSH connection to the VM failed due to insufficient memory allocation (1024MB)
* The VM booted but did not start the SSH service properly, causing connection resets

---

## 🔹 Solution

* Increased VM memory to 4096MB in the `Vagrantfile`
* Restarted the VM using `vagrant reload`

---

## 🔹 Result

* The Spark ETL pipeline executed successfully using `spark-submit`
* Output data was stored in the `output_weather/` directory in Parquet format
* Checked the output using PySpark

Output:

```text
+--------+---------+--------+---------+----------+-----------+---------+-------------+-----------+
|latitude|longitude|timezone|elevation|time      |temperature|windspeed|winddirection|weathercode|
+--------+---------+--------+---------+----------+-----------+---------+-------------+-----------+
|52.52   |13.419998|GMT     |38.0     |2026-05-03|20.9       |7.2      |273          |3          |
+--------+---------+--------+---------+----------+-----------+---------+-------------+-----------+
```

---

## 🔹 Notes

* Spark was executed in local mode within a single-node VM environment
* The processed data was stored in Parquet format as a structured output format commonly used in Spark.
