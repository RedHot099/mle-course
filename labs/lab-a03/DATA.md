# Dane w lab-a03

freshcast-sample.csv zawiera 14 dni jednej serii: sklep 70, produkt 116, od 28 marca do 10 kwietnia 2024. To wycinek publicznego FreshRetailNet-50K, Dingdong-Inc, CC BY 4.0.

Źródło: https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K. Publikacja: Wang, Gu, Long, Li, Shen, Fu, Zhou, Jiang, FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail, arXiv:2505.16319, 2025.

Wartości sale_amount pozostają niezmienione. Kolumnę stock_hour6_22_cnt nazwano stockout_hours. Jednostki sprzedaży pochodzą ze źródła; nie zakładamy liczby sztuk. stockout_hours opisuje godziny niedostępności towaru. Nie jest brakiem pomiaru.

Dni do 3 kwietnia są historią, a 4–10 kwietnia okresem oceny. Cały wycinek był widoczny w A4.2, więc nie stanowi niezależnego holdoutu. Nie zawiera danych klientów. Ten lab nie korzysta z project-holdout.csv.
