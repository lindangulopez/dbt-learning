# **production-style Apache Airflow DAG** for a **Sales Analytics Pipeline**. 

It includes:

* DAG configuration
* Environment parameterization using Airflow Variables
* Retry handling
* SLA monitoring
* Logging
* Failure callbacks
* Three tasks:

  1. Extract sales data
  2. Validate data quality
  3. Process analytics
* Task dependencies
* Environment-aware configuration

Save this file as:

```
dags/sales_analytics_dag.py
```

---

```python
"""
Production Sales Analytics DAG

Workflow:
    Extract Sales Data
            |
            v
    Validate Data Quality
            |
            v
    Process Analytics

Features:
- Environment parameterization
- Retry handling
- SLA monitoring
- Failure alerts
- Logging
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from datetime import datetime, timedelta

import logging


# -------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------

logger = logging.getLogger("sales_pipeline")


# -------------------------------------------------------
# Environment Configuration
# -------------------------------------------------------

ENVIRONMENT = Variable.get(
    "environment",
    default_var="development"
)


if ENVIRONMENT == "production":

    SALES_DATABASE = "production_sales_db"
    SALES_TABLE = "prod_sales"

else:

    SALES_DATABASE = "development_sales_db"
    SALES_TABLE = "dev_sales"


# -------------------------------------------------------
# Failure Callback
# -------------------------------------------------------

def task_failure_alert(context):

    task_instance = context["task_instance"]

    logger.error(
        f"""
        Task Failed:
        DAG: {task_instance.dag_id}
        Task: {task_instance.task_id}
        Execution Date:
        {context.get('execution_date')}
        """
    )


# -------------------------------------------------------
# Default DAG Arguments
# -------------------------------------------------------

default_args = {

    "owner": "data_engineering",

    # Do not depend on previous DAG execution
    "depends_on_past": False,

    # Pipeline start date
    "start_date": datetime(2026, 1, 1),

    # Retry configuration
    "retries": 3,

    "retry_delay": timedelta(
        minutes=5
    ),

    # SLA monitoring
    "sla": timedelta(
        hours=2
    ),

    # Failure handling
    "on_failure_callback":
        task_failure_alert
}


# -------------------------------------------------------
# Task Functions
# -------------------------------------------------------

def extract_sales_data(**context):

    logger.info(
        "Starting sales extraction"
    )

    logger.info(
        f"Environment: {ENVIRONMENT}"
    )

    logger.info(
        f"Database: {SALES_DATABASE}"
    )

    logger.info(
        f"Table: {SALES_TABLE}"
    )


    # Example extraction logic
    sales_records = [
        {
            "id": 1,
            "amount": 200
        },
        {
            "id": 2,
            "amount": 500
        }
    ]


    if len(sales_records) == 0:

        raise Exception(
            "No sales data extracted"
        )


    # Push data information to next task
    context["ti"].xcom_push(
        key="record_count",
        value=len(sales_records)
    )


    logger.info(
        f"Extracted {len(sales_records)} records"
    )



def validate_sales_data(**context):

    logger.info(
        "Starting data validation"
    )


    record_count = context["ti"].xcom_pull(
        task_ids="extract_sales_data",
        key="record_count"
    )


    if record_count == 0:

        raise Exception(
            "Data quality check failed"
        )


    logger.info(
        f"Validation successful. Records: {record_count}"
    )



def process_sales_analytics(**context):

    logger.info(
        "Starting analytics processing"
    )


    record_count = context["ti"].xcom_pull(
        task_ids="extract_sales_data",
        key="record_count"
    )


    analytics_result = {

        "total_records":
            record_count,

        "status":
            "completed"

    }


    logger.info(
        f"Analytics Result: {analytics_result}"
    )



# -------------------------------------------------------
# Create DAG
# -------------------------------------------------------

with DAG(

    dag_id="sales_analytics_production",

    default_args=default_args,

    description=
        "Production sales analytics pipeline",

    # Run daily at 6 AM UTC
    schedule="0 6 * * *",

    # Do not run missed historical jobs
    catchup=False,

    # Prevent duplicate executions
    max_active_runs=1,

    tags=[
        "sales",
        "analytics",
        "production"
    ]

) as dag:


    # ---------------------------------------------------
    # Task 1: Extract
    # ---------------------------------------------------

    extract_sales = PythonOperator(

        task_id=
            "extract_sales_data",

        python_callable=
            extract_sales_data,

        provide_context=True

    )


    # ---------------------------------------------------
    # Task 2: Validate
    # ---------------------------------------------------

    validate_sales = PythonOperator(

        task_id=
            "validate_sales_data",

        python_callable=
            validate_sales_data,

        provide_context=True

    )


    # ---------------------------------------------------
    # Task 3: Analytics
    # ---------------------------------------------------

    process_analytics = PythonOperator(

        task_id=
            "process_sales_analytics",

        python_callable=
            process_sales_analytics,

        provide_context=True

    )


    # ---------------------------------------------------
    # Workflow Dependency
    # ---------------------------------------------------

    extract_sales >> validate_sales >> process_analytics
```

---

## Running the DAG

### 1. Install Airflow

Example:

```bash
pip install apache-airflow
```

---

### 2. Initialize Airflow Database

```bash
airflow db init
```

---

### 3. Create Airflow User

```bash
airflow users create \
--username admin \
--firstname Admin \
--lastname User \
--role Admin \
--email admin@example.com
```

---

### 4. Start Airflow Scheduler

Terminal 1:

```bash
airflow scheduler
```

---

### 5. Start Airflow Web Server

Terminal 2:

```bash
airflow webserver --port 8080
```

Open:

```
http://localhost:8080
```

---

## Create Airflow Variable

In Airflow UI:

```
Admin
 → Variables
 → Add Variable
```

Add:

| Key         | Value      |
| ----------- | ---------- |
| environment | production |

or using CLI:

```bash
airflow variables set environment production
```

---

## Test DAG Manually

Run:

```bash
airflow dags test sales_analytics_production 2026-01-01
```

---

## Production Improvements You Could Add

For a real enterprise pipeline, you would usually replace the example functions with:

* `PostgresOperator` / `SnowflakeOperator` for SQL processing
* Cloud storage operators (S3, GCS, Azure Blob)
* Data quality frameworks like Great Expectations
* Slack/email alert callbacks
* Docker/Kubernetes execution
* Unit tests for DAG validation

This DAG structure follows the production workflow principles: **idempotency, parameterization, observability, retries, SLA monitoring, and graceful failure handling.**
