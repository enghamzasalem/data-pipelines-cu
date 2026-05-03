# Weather Data Pipeline using Spark + Hadoop (HDFS + YARN)

## Project Overview

This project implements a distributed data pipeline using **Apache Spark on Hadoop** to fetch, transform, and store weather data.

The pipeline:
1. Fetches unstructured JSON data from a public weather API
2. Transforms it into a structured format using Spark
3. Validates schema using Python (Pydantic)
4. Stores the processed output in HDFS and locally for verification

---

##  System Architecture

### Hadoop Cluster Design (Vagrant-based)

- **Master Node (192.168.56.10)**
  - NameNode (HDFS metadata manager)
  - ResourceManager (YARN job scheduler)
  - SecondaryNameNode (checkpointing)

- **Worker Node (192.168.56.11)**
  - DataNode (HDFS storage)
  - NodeManager (YARN task execution)

---

## Technologies Used

- Apache Hadoop (HDFS + YARN)
- Apache Spark (PySpark)
- Python 3
- Open-Meteo Weather API
- Vagrant + VirtualBox (cluster setup)

---

## 🔄 Pipeline Workflow

1. **Data Ingestion**
   - API: Open-Meteo
   - Raw JSON weather data is fetched using Python requests

2. **Processing (Spark)**
   - Spark reads raw JSON
   - Data is transformed into structured schema:
     - latitude
     - longitude
     - temperature
     - windspeed
     - weather code
     - conditions description

3. **Validation**
   - Pydantic schema ensures data consistency

4. **Storage**
   - Output saved to:
     - HDFS: `/user/vagrant/weather_structured`
     - Local file: `output.json`

---

## How to Run

```bash
spark-submit --master yarn weather_spark.py
spark-submit --master local[*] weather_spark.py

Output

HDFS Output:

hdfs dfs -ls /user/vagrant/weather_structured

View Data:

hdfs dfs -cat /user/vagrant/weather_structured/part-*

Local Output:

output.json