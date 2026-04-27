## Troubleshooting Summary

### 1. Removal of `days_ago`
In recent Airflow versions (late 2.x+), the `days_ago` function was removed.  
To define the DAG start date, `pendulum.datetime` was used instead.

---

### 2. Replacement of `execution_date`
Newer Airflow versions no longer use `execution_date` in templating.  
It has been replaced with `logical_date`, so the DAG was updated accordingly.

---

### 3. Wikimedia Data Upload Delay (404 Error)
Wikipedia pageview data is uploaded with a delay (approximately 45 minutes to 3 hours).  
Triggering the DAG for very recent timestamps caused a **404 download error** because the file was not yet available on the server.

To resolve this issue, a specific past timestamp was manually provided when triggering the DAG:

```bash
airflow dags trigger lecture4_stocksense_exercise \
  --logical-date 2026-02-28T12:00:00+00:00
