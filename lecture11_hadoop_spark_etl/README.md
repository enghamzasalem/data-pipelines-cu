# Weather ETL Pipeline using Apache Spark

## Overview
This project demonstrates a simple ETL (Extract, Transform, Load) pipeline using Apache Spark inside a Vagrant virtual machine.

## Steps
1. Read raw weather data from JSON file
2. Extract required fields:
   - latitude
   - longitude
   - temperature_2m
3. Transform nested JSON into flat structure
4. Write output as Parquet file

## Technologies Used
- Apache Spark
- Python (PySpark)
- Vagrant
- VirtualBox

## How to Run
```bash
vagrant up
vagrant ssh
cd /vagrant
spark-submit scripts/weather_etl.py