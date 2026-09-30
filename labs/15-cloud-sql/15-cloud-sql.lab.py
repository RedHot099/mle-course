# %% [markdown]
# # Lab 15: bucket, publikacja modelu i SQL nad plikami
#
# Tickety są w `README.md` tego katalogu. Ten notebook łączy się z lokalnym serwerem S3, przenosi dane i model do bucketu i zadaje SQL-em pytania, które wcześniej zadawałeś w pandas.

# %%
import os
import socket
import time

import pandas as pd

from coursekit import paths
from coursekit.nb import check

os.chdir(paths.ROOT)
# The local server accepts any pair of keys, but requests must be signed.
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")
PORT = 9000


def answers_s3(endpoint):
    """Tell whether an S3 server at `endpoint` accepts our local keys."""
    import boto3

    try:
        boto3.client("s3", endpoint_url=endpoint, region_name="us-east-1").list_buckets()
    except Exception:  # noqa: BLE001 - any failure means "not usable"
        return False
    return True


def port_is_taken(port):
    """Tell whether something listens on localhost:port."""
    with socket.socket() as probe:
        probe.settimeout(0.5)
        return probe.connect_ex(("127.0.0.1", port)) == 0


ENDPOINT = f"http://localhost:{PORT}"
if answers_s3(ENDPOINT):
    print("Serwer S3 działa na", ENDPOINT)
else:
    if port_is_taken(PORT):
        print(f"Na porcie {PORT} działa coś innego, co nie przyjmuje lokalnych kluczy.")
        PORT = next(port for port in range(9001, 9100) if not port_is_taken(port))
    # Fallback: the same moto server, inside this process. It stops with the kernel.
    import logging

    from moto.server import ThreadedMotoServer

    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # one log line per request otherwise
    local_server = ThreadedMotoServer(ip_address="127.0.0.1", port=PORT, verbose=False)
    local_server.start()
    ENDPOINT = f"http://localhost:{PORT}"
    print("Serwer S3 uruchomiony w notebooku na", ENDPOINT)

# %%
check("15")

# %% [markdown]
# ## Bucket i pliki
#
# Serwis z ticketu 15.3 na lokalnym serwerze. Dane przetworzone z modułu 07 trafiają do bucketu pod prefiksem `processed/`.

# %%
from freshcast.config import StorageSettings
from freshcast.storage.s3 import S3Storage

settings = StorageSettings(bucket="freshcast-lab", endpoint_url=ENDPOINT)
storage = S3Storage.from_settings(settings, cache_dir=paths.DATA_DIR / "cache")
storage.ensure_bucket()

# >>> SOLUTION 15.3
for name in ["daily.parquet", "store_dim.parquet", "product_dim.parquet"]:
    storage.upload_file(paths.PROCESSED_DIR / name, f"processed/{name}")
keys = storage.list_keys("processed/")
# --- STUB
#| keys = ...
# <<< SOLUTION
print(keys)
print("exists('processed'):", storage.exists("processed"), " exists('processed/daily.parquet'):", storage.exists("processed/daily.parquet"))

# %% [markdown]
# ## Cache
#
# Pierwsze `fetch` pobiera plik, drugie tylko pyta serwer, czy obiekt się zmienił.

# %%
# >>> SOLUTION 15.4
timings = []
for attempt in range(2):
    start = time.perf_counter()
    local_copy = storage.fetch("processed/daily.parquet")
    timings.append(time.perf_counter() - start)
# --- STUB
#| timings = ...
# <<< SOLUTION
print(f"Pierwsze pobranie {timings[0] * 1000:.0f} ms, drugie {timings[1] * 1000:.0f} ms: {local_copy.relative_to(paths.ROOT)}")

# %% [markdown]
# ## Publikacja modelu
#
# Ten sam `train` co w module 14, ale z sekcją `storage` ustawioną przez zmienne środowiskowe, bez edycji pliku konfiguracji. Po treningu model trafia do bucketu. Potem pobierasz go z powrotem, tak jak zrobiłby serwer prognoz.

# %%
from freshcast import pipeline
from freshcast.artifacts import load_model
from freshcast.config import load_settings
from freshcast.storage.s3 import fetch_model

profile = paths.active_profile().name
config = paths.ROOT / "configs" / f"{'standard' if profile == 'full' else profile}.yaml"
os.environ["FRESHCAST_STORAGE__BUCKET"] = "freshcast-lab"
os.environ["FRESHCAST_STORAGE__ENDPOINT_URL"] = ENDPOINT
run_settings = load_settings(config)

# >>> SOLUTION 15.5
result = pipeline.train(run_settings)
signature = result.model_dir.name
published = storage.list_keys(f"models/{signature}/")
downloaded = fetch_model(storage, signature, paths.DATA_DIR / "downloaded-models", prefix="models")
model, metadata = load_model(downloaded)
# --- STUB
#| published = ...
#| downloaded = ...
# <<< SOLUTION
del os.environ["FRESHCAST_STORAGE__BUCKET"], os.environ["FRESHCAST_STORAGE__ENDPOINT_URL"]
print("\n".join(published))
print("Pobrany model:", metadata["signature"], type(model).__name__)

# %% [markdown]
# ## SQL nad plikiem
#
# DuckDB czyta parquet bezpośrednio. Te same pytania, co w modułach 06-07.

# %%
from datetime import date

from freshcast.storage import sql

con = sql.connect()
DAILY = paths.PROCESSED_DIR / "daily.parquet"
city = int(pd.read_parquet(DAILY, columns=["city_id"])["city_id"].iloc[0])

print(sql.city_sales(con, DAILY, city, date(2024, 6, 1), date(2024, 6, 7)).head())
sql.store_summary(con, DAILY).head()

# %%
sql.category_sales(
    con, DAILY, paths.PROCESSED_DIR / "store_dim.parquet", paths.PROCESSED_DIR / "product_dim.parquet", min_products=50
).head()

# %%
sql.top_products_per_store(con, DAILY, top=3).head(9)

# %% [markdown]
# Funkcje okna obok ich odpowiedników w pandas z modułu 07. Czy dają te same liczby?

# %%
from freshcast.data.panel import add_lag, add_rolling_mean
from freshcast.data.prepare import load_processed

panel = load_processed(paths.PROCESSED_DIR)
# >>> SOLUTION 15.8
lag_sql = sql.sales_lag(con, DAILY, 7)["sale_amount_lag_7"].to_numpy()
lag_pandas = add_lag(panel, "sale_amount", 7)["sale_amount_lag_7"].to_numpy()
mean_sql = sql.rolling_mean_7(con, DAILY)["sale_amount_mean_7_lag_1"].to_numpy()
mean_pandas = add_rolling_mean(panel, "sale_amount", 7)["sale_amount_mean_7_lag_1"].to_numpy()
# --- STUB
#| lag_sql, lag_pandas, mean_sql, mean_pandas = ...
# <<< SOLUTION
import numpy as np

print("lag 7 zgodny:", np.allclose(lag_sql, lag_pandas, equal_nan=True))
print("średnia 7 dni zgodna:", np.allclose(mean_sql, mean_pandas, equal_nan=True))

# %% [markdown]
# ## SQL prosto z bucketu
#
# To samo zapytanie, ale plik leży w buckecie. DuckDB potrzebuje rozszerzenia `httpfs` (pobiera je raz, przy pierwszym użyciu) i adresu serwera: `connect` ustawia to z ustawień.

# %%
s3_con = sql.connect(settings)
start = time.perf_counter()
from_bucket = sql.store_summary(s3_con, "s3://freshcast-lab/processed/daily.parquet")
print(f"{len(from_bucket)} sklepów, {time.perf_counter() - start:.2f} s")
print("Ten sam wynik co z dysku:", from_bucket.equals(sql.store_summary(con, DAILY)))

# %% [markdown]
# ## Pytania
#
# Bez sprawdzeń. Odpowiedz krótko.
#
# 1. `exists("processed")` zwraca `False`, choć w buckecie są klucze zaczynające się od `processed/`. Dlaczego to poprawne zachowanie?
# 2. Co musiałbyś zmienić w kodzie, żeby zamiast lokalnego serwera używać prawdziwego Amazon S3? Co zmieniłbyś poza kodem?
# 3. Dlaczego `metadata.json` jest wysyłany na końcu, a `fetch_model` najpierw pobiera do katalogu tymczasowego?
# 4. Kiedy wolisz SQL w DuckDB, a kiedy pandas? Podaj po jednej sytuacji.
#
# *Twoje odpowiedzi:*
