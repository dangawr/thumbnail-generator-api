## API Paths

### images/
**Allowed Methods** : GET, POST
**Access Level** : Authenticated Users

Endpoint for list and upload images

### images/
**Allowed Methods** : GET, POST
**Access Level** : Authenticated Users

Endpoint for list and upload images






## Technologies Used
- Django
- Django Rest Framework
- Docker
- Postgres

## How to run:
- Before first run, you have to add starter pack of tiers (Basic, Premium, Enterprise). To do this please run command:
```
docker-compose run --rm app sh -c "python manage.py loaddata tiers.json"
```
- To run application:
```
docker-compose up
```
- To run tests:
```
docker-compose run --rm app sh -c "python manage.py test"
```
