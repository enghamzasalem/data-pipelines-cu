For this exercise, I built an ETL pipeline using Apache Airflow.  
The pipeline downloads hourly Wikipedia pageview data in order to extract the number of views for several tech companies.

The companies under observation include Google, Amazon, Apple, Microsoft, and Facebook.

# Pipeline Assignments The results are saved into a CSV file and then kept in a SQLite database.

The DAG consists of four tasks:**get_data → extract_gz → fetch_pageviews → add_to_db**

- **get_data** downloads the hourly Wikipedia pageviews `.gz` file using the execution date.
- **extract_gz** extracts the downloaded gzip file using a BashOperator.

After reading the extracted file and filtering pageviews for the tracked companies, **fetch_pageviews** saves the results into a CSV file.
After reading the CSV file, **add_to_db** inserts the records into a SQLite database.