# 🚀 GCP Data Pipeline: CoinMarketCap to BigQuery

This project implements a data pipeline on the Google Cloud Platform (GCP) to fetch cryptocurrency data from the CoinMarketCap API, store it in Google Cloud Storage (GCS), and load it into a BigQuery table for analysis. The pipeline is orchestrated using Apache Airflow on Cloud Composer.

---

## 🏗️ Architecture Overview

The pipeline follows these steps:

1.  **Orchestration**: An Airflow DAG running on **Cloud Composer** triggers the pipeline.
2.  **Data Extraction**: A Docker container is launched using the `KubernetesPodOperator`. This container runs a Python script to fetch the latest cryptocurrency listings from the **CoinMarketCap API**.
3.  **Data Storage**: The Python script processes the raw JSON data and saves it as a CSV file in a specified **Google Cloud Storage** bucket.
4.  **Data Loading**: Once the extraction is complete, the Airflow DAG executes a SQL script to load the CSV data from GCS into a raw **BigQuery** table, which serves as the initial landing zone for the data.

---

## 📁 Repository Structure

Here is the recommended layout for the project files. This structure separates the data extraction application from the orchestration (Airflow) components.

```
/
├── README.md
├── coinmarketcap_fetcher/
│   ├── Dockerfile
│   ├── api_json_to_csv.py
│   └── requirements.txt
└── composer/
    └── dags/
        ├── my_dag.py
        └── load_to_bronze.sql
```

* **`coinmarketcap_fetcher/`**: Contains the Python application responsible for fetching the data.
    * `Dockerfile`: Instructions to build the container image for the fetcher script.
    * `api_json_to_csv.py`: The core Python script that calls the API and uploads the CSV to GCS.
    * `requirements.txt`: Python package dependencies.
* **`composer/dags/`**: Contains the Airflow DAG and related SQL scripts.
    * `my_dag.py`: The main DAG file that defines the pipeline tasks and their dependencies.
    * `load_to_bronze.sql`: The SQL script used by BigQuery to load the CSV from GCS.

---

## ✅ Prerequisites

Before you begin, ensure you have the following:

* A Google Cloud Platform project.
* Google Cloud SDK (gcloud) installed and configured.
* Docker installed locally.
* A Cloud Composer environment set up in your GCP project.
* Your CoinMarketCap API Key.

---

## 🛠️ Setup and Deployment

Follow these steps to configure your GCP environment and deploy the pipeline.

### 1. Configure GCP Environment

**Enable APIs**
Ensure the following APIs are enabled in your GCP project:
* Cloud Composer API (`composer.googleapis.com`)
* Google Kubernetes Engine API (`container.googleapis.com`)
* Secret Manager API (`secretmanager.googleapis.com`)
* BigQuery API (`bigquery.googleapis.com`)
* Cloud Storage API (`storage-component.googleapis.com`)

**Create GCS Bucket**
Create a GCS bucket to store the output CSV file. Your Cloud Composer environment will also have its own bucket for DAGs.

**Store API Key in Secret Manager**
Securely store your CoinMarketCap API key in Google Secret Manager.

**Configure Service Account Permissions**
The default service account for Compute Engine (used by the GKE nodes in your Composer environment) needs permission to access the secret.

1.  Go to the **IAM & Admin** page in the GCP Console.
2.  Find the **Compute Engine default service account**.
3.  Grant it the **Secret Manager Secret Accessor** (`roles/secretmanager.secretAccessor`) role.
4.  Ensure it also has **Storage Object Admin** (`roles/storage.objectAdmin`) to write to the GCS bucket.

**Create BigQuery Dataset**
Create a BigQuery dataset to hold your table.

### 2. Build and Push the Docker Image

Navigate to the `coinmarketcap_fetcher` directory and run the following commands to build the Docker image and push it to Google Container Registry (GCR).

```bash
# Authenticate Docker with GCR
gcloud auth configure-docker

# Build the image
docker build -t gcr.io/your_project_id/coinmarketcap-fetcher:latest .

# Push the image to GCR
docker push gcr.io/your_project_id/coinmarketcap-fetcher:latest
```

### 3. Deploy Airflow DAGs

1.  **Update Configuration**: Before uploading, you may need to update the project ID, bucket names, and dataset/table names in `api_json_to_csv.py`, `my_dag.py`, and `load_to_bronze.sql` to match your environment.
2.  **Upload to Composer**: Upload the contents of the `composer/dags/` directory to the `dags` folder in your Cloud Composer's GCS bucket.

---

## ▶️ Usage

1.  Open the **Airflow UI** for your Cloud Composer environment.
2.  Find the `coinmarketcap_dag` on the DAGs list and enable it.
3.  You can trigger the DAG manually by clicking the "Play" button.
4.  Monitor the progress of the DAG run in the Grid View. You can view logs for each task, including the output from the `KubernetesPodOperator`.
5.  Once the DAG completes successfully, you can query the data in your BigQuery table.
