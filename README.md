# coorseo-api

## Pierwsze uruchomienie

### Użycie `docker-compose`

1. Pobranie obrazów:
```bash
docker-compose pull
```

2. Uruchomienie usług:
```bash
docker-compose up -d
```

3. Inicjalizacja struktury bazy danych:
```bash
docker-compose exec application python application/models/models.py
```