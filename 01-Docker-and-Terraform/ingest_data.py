import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

parse_dates_green = ["lpep_pickup_datetime", "lpep_dropoff_datetime"]

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-password', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default='5432', help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database')
@click.option('--pg-year', default='2021', help='Year for taxi data')
@click.option('--pg-month', default='01', help='Month for taxi data')
@click.option('--yellow-target-table', default='yellow_taxi_data', help='Yellow taxi table name')
@click.option('--green-target-table', default='green_taxi_data', help='Green taxi table name')
def run(pg_user, pg_password, pg_host, pg_port, pg_db, pg_year, pg_month, yellow_target_table, green_target_table):


    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = prefix + (f"yellow_tripdata_{pg_year}-{pg_month}.csv.gz")
    df = pd.read_csv(url, dtype=dtype, parse_dates=parse_dates)
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    print(pd.io.sql.get_schema(df, name=yellow_target_table, con=engine))

    

    df.head(n=0).to_sql(name=yellow_target_table, con=engine, if_exists='replace')

    df_iter = pd.read_csv(
    url,
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
    )


    first = True

    for df_chunk in tqdm(df_iter):
        if first:
        # Create table schema (no data)
            df_chunk.head(0).to_sql(
            name=yellow_target_table,
            con=engine,
            if_exists="replace"
            )
            first = False
            print("Table created")

        # Insert chunk
        df_chunk.to_sql(
        name=yellow_target_table,
        con=engine,
        if_exists="append"
        )

        print("Inserted:", len(df_chunk))
    

    green_taxi_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/'
    green_taxi_url = green_taxi_prefix + (f'green_tripdata_{pg_year}-{pg_month}.csv.gz')
    green_df = pd.read_csv(green_taxi_url, dtype=dtype, parse_dates=parse_dates_green)


    print(pd.io.sql.get_schema(green_df, name=green_target_table, con=engine))
    green_df.head(n=0).to_sql(name=green_target_table, con=engine, if_exists='replace')
    green_df.to_sql(
    name=green_target_table,
    con=engine,
    if_exists="replace",
    index=False
    )
    print(f'inserted successfully {len(green_df)}')


if __name__ == '__main__':
    run()

