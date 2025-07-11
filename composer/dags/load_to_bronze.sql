CREATE OR REPLACE TABLE `learn-gcloud-462613.bronze.bronze_crypto_prices`
(
    id INT64,
    name STRING,
    symbol STRING,
    slug STRING,
    cmc_rank INT64,
    num_market_pairs INT64,
    circulating_supply FLOAT64,
    total_supply FLOAT64,
    max_supply FLOAT64,
    price_usd FLOAT64,
    volume_24h_usd FLOAT64,
    percent_change_1h FLOAT64,
    percent_change_24h FLOAT64,
    percent_change_7d FLOAT64,
    market_cap_usd FLOAT64,
    last_updated TIMESTAMP,
    retrieved_timestamp TIMESTAMP
);

LOAD DATA INTO `learn-gcloud-462613.bronze.bronze_crypto_prices`
FROM FILES (
    format = 'CSV',
    uris = ['gs://dev-file-dump/crypto_prices.csv'],
    skip_leading_rows = 1
);
