# dbt Analytics Engineering Project

## Overview

This repository contains my first dbt (Data Build Tool) project developed as part of my analytics engineering learning journey. The project demonstrates modern data transformation practices using SQL, modular modeling, testing, and documentation.

The goal of this repository is to build clean, maintainable data models while following analytics engineering best practices.

## Project Goals

* Learn and apply dbt fundamentals
* Build modular SQL data models
* Implement data quality tests
* Generate project documentation
* Practice version control using Git and GitHub
* Develop a portfolio project that demonstrates analytics engineering skills

## Technologies

* dbt Core
* SQL
* Git
* GitHub
* Python
* Jinja

## Project Structure

```text
models/          SQL transformation models
macros/          Reusable Jinja macros
seeds/           Seed data
snapshots/       Snapshot models
tests/           Data quality tests
analyses/        Exploratory SQL analyses
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/lindangulopez/<repository-name>.git
```

Create and activate a Python virtual environment:

```bash
python -m venv dbt-env

# macOS/Linux
source dbt-env/bin/activate

# Windows
dbt-env\Scripts\activate
```

Install dbt and project dependencies:

```bash
pip install dbt-core
dbt deps
```

Run the project:

```bash
dbt run
```

Run tests:

```bash
dbt test
```

Generate documentation:

```bash
dbt docs generate
dbt docs serve
```

## Learning Objectives

This repository documents my progress as I continue learning analytics engineering concepts, including:

* Data modeling
* Data transformation
* SQL best practices
* Data testing
* Documentation
* Git workflows
* Analytics engineering principles

## Future Improvements

* Add additional dbt models
* Implement incremental models
* Create custom macros
* Expand automated testing
* Add CI/CD with GitHub Actions
* Integrate a cloud data warehouse

## Author

**Linda Angulo Lopez**

I am building this repository as part of my journey into analytics engineering and modern data transformation, on [coursera](https://www.coursera.org/professional-certificates/open-source-data-engineering-with-spark-dbt-and-airflow).
