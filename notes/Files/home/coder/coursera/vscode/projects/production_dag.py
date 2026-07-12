"""
Production-Ready Airflow DAG for Daily Sales Pipeline
Course: Automate Data Workflows with Airflow Excellence
Module 2: Production Implementation - Core Application & Assessment

This DAG demonstrates enterprise-grade workflow design principles
used by companies like Airbnb, Uber, and Netflix for production data pipelines.

NOTE FOR LEARNERS:
This lab runs in a simulated Apache Airflow environment.
Some APIs (such as schedule_interval, days_ago, and task-level SLA callbacks)
have been updated in newer Airflow versions.
"""

from datetime import datetime, timedelta

# UPDATED IMPORTS (required for simulated Airflow environment)
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


# ===================================================
# PROVIDED CODE - DO NOT MODIFY
# ===================================================

def extract_sales_data(**context):
    """Simulate daily sales data extraction from multiple sources"""
    print("Extracting sales data from CRM, POS, and web analytics...")
    print("Data extraction completed successfully")
    return "sales_data_extracted"


def transform_customer_metrics(**context):
    """Transform and aggregate customer sales metrics"""
    print("Transforming sales data into customer metrics...")
    print("Calculating daily revenue, customer counts, and conversion rates...")
    return "metrics_transformed"


def load_to_warehouse(**context):
    """Load processed data to data warehouse"""
    print("Loading transformed metrics to data warehouse...")
    print("Data loaded successfully to production tables")
    return "data_loaded"


def validate_data_quality(**context):
    """Validate loaded data meets quality thresholds"""
    print("Running data quality checks...")
    print("All quality checks passed")
    return "validation_complete"


def send_slack_alert(context):
    """Send Slack notification for task failure (simulated)"""
    print(
        f"TASK FAILURE: DAG={context['dag'].dag_id}, "
        f"Task={context['task_instance'].task_id}"
    )
    print("Alert sent to #data-engineering Slack channel")


# ===================================================
# SLA CALLBACK
# ===================================================
# PRACTICE CHALLENGE 3
#
# TASK:
# Configure SLA monitoring with Slack alert callback
#
# In production this would call Slack API.
# In this lab it prints a simulated alert.
#

def sla_alert_callback(
    dag,
    task_list,
    blocking_task_list,
    slas,
    blocking_tis
):

    print("==============================")
    print("SLA MISSED ALERT")
    print(f"DAG: {dag.dag_id}")
    print(f"Tasks: {task_list}")
    print("Alert sent to #data-engineering Slack channel")
    print("==============================")


# ===================================================
# PRACTICE CHALLENGE 1
# ===================================================
# TASK: Configure the DAG's default_args with production-ready retry settings
# (3 retries, 5-minute delay) and email notifications
#
# Include:
# - retries
# - retry_delay
# - email_on_failure
# - email_on_retry
# - owner
#
# Expected Outcome:
# DAG configured with robust failure handling defaults
#
# YOUR CODE HERE


default_args = {

    # Workflow ownership
    "owner": "data-engineering",

    # Do not depend on previous DAG execution
    "depends_on_past": False,

    # Retry transient failures
    "retries": 3,

    # Initial retry delay
    "retry_delay": timedelta(minutes=5),

    # Increase delay between retries
    # Retry 1 -> 5 minutes
    # Retry 2 -> 10 minutes
    # Retry 3 -> 20 minutes
    "retry_exponential_backoff": True,

    # Prevent unlimited retry delays
    "max_retry_delay": timedelta(hours=1),

    # Email notifications
    "email_on_failure": True,

    "email_on_retry": True,

    # Failure alert callback
    "on_failure_callback": send_slack_alert

}


# ===================================================
# PRACTICE CHALLENGE 2
# ===================================================
# TASK: Create the DAG with appropriate scheduling and configuration
# Use dag_id='daily_sales_pipeline', schedule daily at 2 AM,
# and include catchup=False
#
# YOUR CODE HERE


dag = DAG(

    dag_id="daily_sales_pipeline",

    default_args=default_args,

    description="Production daily sales pipeline",

    # Run every day at 2 AM
    schedule="0 2 * * *",

    start_date=datetime(2024, 1, 1),

    catchup=False,

    # ===================================================
    # PRACTICE CHALLENGE 3
    # ===================================================
    # Configure SLA callback at DAG level
    #
    sla_miss_callback=sla_alert_callback,

    tags=[
        "sales",
        "production"
    ]

)


# ===================================================
# PROVIDED CODE - Task Definitions (DO NOT MODIFY)
# ===================================================


# ===================================================
# PRACTICE CHALLENGE 3
# ===================================================
# TASK:
# Configure SLA monitoring:
#
# Extraction task:
# 30 minutes
#
# Transformation task:
# 45 minutes
#
# YOUR CODE HERE


extract_task = PythonOperator(

    task_id="extract_sales_data",

    python_callable=extract_sales_data,

    sla=timedelta(minutes=30),

    dag=dag

)


transform_task = PythonOperator(

    task_id="transform_customer_metrics",

    python_callable=transform_customer_metrics,

    sla=timedelta(minutes=45),

    dag=dag

)


load_task = PythonOperator(

    task_id="load_to_warehouse",

    python_callable=load_to_warehouse,

    dag=dag

)


validate_task = PythonOperator(

    task_id="validate_data_quality",

    python_callable=validate_data_quality,

    dag=dag

)


# ===================================================
# PRACTICE CHALLENGE 2
# ===================================================
# TASK:
# Implement task dependencies so that:
#
# - extract_task runs first
# - transform_task waits for extract_task
# - load_task and validate_task run in parallel after transform_task
#
# Hint:
# Use >> operators
#
# Expected Outcome:
# Logical task execution order with parallel optimization


extract_task >> transform_task >> [load_task, validate_task]