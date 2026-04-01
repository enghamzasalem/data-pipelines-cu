## Troubleshooting Summary

1. **days_ago issue**  
   In the current Airflow version, `days_ago` is deprecated.  
   The DAG start date was defined using `pendulum.datetime` instead.

---

2. **fs_default error**  
   `FileSensor` failed because the `fs_default` connection was not defined.  
   This was resolved by creating the default filesystem connection:

   ```bash
   airflow connections add fs_default \
       --conn-type fs \
       --conn-extra '{"path": "/"}'

---

3. **PosixPath serialization error**  
   The task returned a `Path` object, which Airflow could not serialize in XCom.  
   This was fixed by returning the path as a string (`return str(output_path)`).
