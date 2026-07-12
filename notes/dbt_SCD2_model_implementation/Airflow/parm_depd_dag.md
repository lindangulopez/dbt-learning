# Memo: Airflow ETL Pipeline Parameterization and DAG Dependency Design

## Parameterization

Parameterization allows the same Airflow DAG code to run across different environments by separating **configuration values**, which change between environments, from **workflow logic**, which remains the same.

For example, a development environment may use a test database, smaller datasets, and reduced resources, while a production environment uses the real data warehouse and production-level resources. Instead of modifying the DAG code manually for each environment, parameters and configuration values can be provided externally.

This approach improves deployment consistency because the same DAG can be promoted from development to production without changing the underlying workflow logic.

### Using Airflow Variables

One approach is to store environment-specific values using Airflow Variables. The DAG retrieves these values dynamically at runtime.

Example:

```python
from airflow.models import Variable

environment = Variable.get("environment", default_var="dev")

if environment == "prod":
    database = "production_sales_db"
else:
    database = "development_sales_db"
```

The same DAG code can then be deployed to multiple Airflow environments while using different configurations.

Development environment:

```
environment = dev
database = development_sales_db
```

Production environment:

```
environment = prod
database = production_sales_db
```

The workflow code remains unchanged; only the configuration values differ.

### Using Environment Variables

Another approach is to use operating system environment variables. These are often managed by deployment systems and allow the DAG to adapt automatically.

Example:

```python
import os

ENVIRONMENT = os.environ.get("AIRFLOW_ENV", "dev")

if ENVIRONMENT == "prod":
    DATA_PATH = "/data/production/sales"
else:
    DATA_PATH = "/data/dev/sales"
```

The deployment environment defines the value:

Development:

```bash
export AIRFLOW_ENV=dev
```

Production:

```bash
export AIRFLOW_ENV=prod
```

The DAG code remains identical in both environments.

### Using DAG Parameters

Airflow also supports runtime parameters that can be supplied when triggering a DAG manually or through automation.

Example:

```python
from airflow import DAG
from airflow.models.param import Param

with DAG(
    dag_id="sales_pipeline",
    params={
        "source": Param("dev_sales", type="string")
    }
) as dag:
    ...
```

This allows users or automated systems to provide values without modifying the DAG source code.

### Benefits of Parameterization

Parameterization provides several advantages:

* **Code reuse:** A single DAG can operate across multiple environments.
* **Lower risk:** Reduces manual code changes between development and production.
* **Simpler deployments:** Environment-specific configuration is managed separately from workflow logic.
* **Better maintainability:** Business logic remains consistent while configuration can change independently.

### Parameterized Environment Architecture

```
                 Same DAG code
                       |
        --------------------------------
        |                              |
 Development Airflow            Production Airflow
        |                              |
 Variables: dev values          Variables: prod values
        |                              |
 Test database                  Production warehouse
```

In practice, environment-specific settings should be managed through Airflow Variables, connections, secrets management systems, or deployment configuration. This approach makes pipelines easier to test, promote, and maintain.

---

# DAG Dependency Design

A well-designed ETL dependency structure ensures that data moves through the pipeline only after each quality checkpoint succeeds. Dependencies should protect data integrity while allowing efficient execution when tasks are independent.

The recommended workflow structure is:

```
extract_sales
       |
       ↓
validate_data
       |
       ↓
transform_sales
       |
       ↓
load_analytics
```

The Airflow dependency definition is:

```python
extract_sales >> validate_data >> transform_sales >> load_analytics
```

## 1. Extract → Validate

The first dependency ensures that validation only occurs after successful data extraction.

```python
extract_sales >> validate_data
```

This prevents invalid or incomplete data from entering later stages.

For example:

* Database connection failure → `extract_sales` fails → validation does not run.
* Missing source file → downstream processing is blocked.

Airflow automatically prevents dependent tasks from executing when an upstream task fails.

---

## 2. Validate → Transform

Validation acts as a data quality checkpoint before transformation.

```python
validate_data >> transform_sales
```

The validation task can check:

* Whether the input file exists.
* Whether the expected number of records were extracted.
* Whether required columns are present.
* Whether critical fields contain valid values.
* Whether data types match expectations.

Example:

```
Extracted data:
100,000 rows ✅
Required columns present ✅
        |
        ↓
Transform starts
```

If validation fails:

```
Extracted data:
0 rows ❌
        |
        ↓
Transform blocked
```

This prevents incorrect data from being processed further.

---

## 3. Transform → Load

The loading step should only execute after successful transformation.

```python
transform_sales >> load_analytics
```

This ensures that only cleaned and processed data reaches the analytics database.

Example:

```
Raw sales data
      ↓
Cleaned sales data
      ↓
Analytics warehouse
```

---

## 4. Parallel Execution Where Appropriate

Not every task needs to run sequentially. Independent workflows can execute in parallel to reduce processing time.

Example:

```
              extract_sales
                    |
        ------------------------
        |                      |
 validate_sales        validate_customers
        |                      |
 transform_sales       transform_customers
        |                      |
        ------------------------
                    |
             load_analytics
```

Airflow can execute independent branches simultaneously, improving pipeline efficiency.

---

## 5. Failure Handling

Each task should include retry policies and monitoring.

Example:

```python
default_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5)
}
```

This provides:

* Automatic recovery from temporary failures.
* Safe stopping of the pipeline when failures persist.
* Notifications when manual intervention is required.

---

# Final ETL Design

The final dependency structure is:

```python
extract_sales >> validate_data >> transform_sales >> load_analytics
```

This design provides:

✅ **Data integrity** — invalid data is prevented from reaching production systems.
✅ **Controlled failure propagation** — only dependent tasks are stopped when failures occur.
✅ **Efficient execution** — independent tasks can run in parallel when appropriate.
✅ **Maintainability** — each pipeline stage has a clear responsibility.

This dependency pattern follows a common production ETL architecture:

**Extract → Quality Gate → Transform → Publish**

Combined with parameterization, this design creates an adaptable, reliable, and maintainable Airflow pipeline that can move safely from development to production environments.
