# coorseo-api

## Użycie docker

```shell script
sudo docker container run \
    --name csob \
    -e SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:TC2m1M2m@cso-demo-database-1.ccjheeugnvft.eu-central-1.rds.amazonaws.com:5432/coorseo \
    -e SECRET_KEY=HxGIR23yK41si8zd9t9kKTEzQu5IyWetsGzrKtPCe294P4ACyselq4McFarahci \
    -e SESSION_COOKIE_NAME=my_cookie \
    -e FLASK_ENV=production \
    -e TESTING=false \
    -p 5000:5000 \
    -d \
    coorseoadmin/coorseo-backend:develop
```

## Użycie `docker-compose`

### Pierwsze uruchomienie

#### Pobranie obrazów:

```bash
docker-compose pull
```

#### Uruchomienie usług:

```bash
docker-compose up -d
```

#### Inicjalizacja struktury bazy danych:

```bash
docker-compose exec application python setup.py
```

### Usunięcie danych aplikacji

#### Zatrzymanie i usunięcie dysków:

```bash
docker-compose down -v
```


## TechDept

## Linki

[Przykład zastosowania PyKafka](https://github.com/code-and-dogs/liveMaps/blob/master/busdata1.py)
