# coorseo-api

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
