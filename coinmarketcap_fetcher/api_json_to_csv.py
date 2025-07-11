from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from datetime import datetime, timezone
from google.cloud import secretmanager
from google.cloud import storage


df = None
data = None


def define_schema():
    global df
    df = pd.DataFrame(columns=[
        'id',
        'name',
        'symbol',
        'slug',
        'cmc_rank',
        'num_market_pairs',
        'circulating_supply',
        'total_supply',
        'max_supply',
        'price_usd',
        'volume_24h_usd',
        'percent_change_1h',
        'percent_change_24h',
        'percent_change_7d',
        'market_cap_usd',
        'last_updated',
        'retrieved_timestamp'
    ])


def fetch_json():
    global data
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': 'USD'
    }

    project_id = "learn-gcloud-462613"
    secret_id = "coinmarketcap_api_key"
    api_key = get_secret(secret_id, project_id)

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)['data']
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def load_df():
    global df, data
    normalized_data = []
    for item in data:
        row = {
            'id': item['id'],
            'name': item['name'],
            'symbol': item['symbol'],
            'slug': item['slug'],
            'cmc_rank': item['cmc_rank'],
            'num_market_pairs': item['num_market_pairs'],
            'circulating_supply': item['circulating_supply'],
            'total_supply': item['total_supply'],
            'max_supply': item.get('max_supply'),
            'price_usd': item['quote']['USD']['price'],
            'volume_24h_usd': item['quote']['USD']['volume_24h'],
            'percent_change_1h': item['quote']['USD']['percent_change_1h'],
            'percent_change_24h': item['quote']['USD']['percent_change_24h'],
            'percent_change_7d': item['quote']['USD']['percent_change_7d'],
            'market_cap_usd': item['quote']['USD']['market_cap'],
            'last_updated': pd.to_datetime(item['last_updated']),
            'retrieved_timestamp': datetime.now(timezone.utc).isoformat()
        }
        normalized_data.append(row)

    df = pd.DataFrame(normalized_data)

    df = df.astype({
        'id': 'int64',
        'name': 'string',
        'symbol': 'string',
        'slug': 'string',
        'cmc_rank': 'int64',
        'num_market_pairs': 'int64',
        'circulating_supply': 'float64',
        'total_supply': 'float64',
        'max_supply': 'float64',
        'price_usd': 'float64',
        'volume_24h_usd': 'float64',
        'percent_change_1h': 'float64',
        'percent_change_24h': 'float64',
        'percent_change_7d': 'float64',
        'market_cap_usd': 'float64',
        'retrieved_timestamp': 'string'
    })


def export_csv():
    global df
    file_name = "crypto_prices.csv"
    
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    client = storage.Client()
    bucket = client.bucket('dev-file-dump')
    blob = bucket.blob(file_name)
    blob.upload_from_string(csv_bytes, content_type='text/csv')

    print(f"Uploaded DataFrame CSV to GCS bucket")


def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value


def main():
    define_schema()
    fetch_json()
    load_df()
    export_csv()


if __name__ == "__main__":
    main()
