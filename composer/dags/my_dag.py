from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 7, 11),
    'retries': 0,
}

with DAG(
    dag_id='coinmarketcap_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    run_container = KubernetesPodOperator(
        task_id='run_coinmarketcap_container',
        namespace='default',
        name='coinmarketcap-fetcher',
        image='gcr.io/learn-gcloud-462613/coinmarketcap-fetcher:latest',
        on_finish_action="delete_pod",
        get_logs=True,
        kubernetes_conn_id='kubernetes_default',
    )

    load_to_bq_bronze = BigQueryInsertJobOperator(
        task_id='load_csv_to_bq_bronze',
        configuration={
            "query": {
                "query": "{% include 'load_to_bronze.sql' %}",
                "useLegacySql": False
            }
        },
        location='US',
        gcp_conn_id='google_cloud_default'
    )

    run_container >> load_to_bq_bronze
