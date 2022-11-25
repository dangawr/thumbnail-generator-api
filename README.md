## API Paths

### images/
<br>**Allowed Methods** : GET, POST
<br>**Access Level** : Authenticated Users

<br>Endpoint for list and upload images.

### images/get-temp-link/
<br>**Allowed Methods** : GET, POST
<br>**Access Level** : Permitted Users (ex. Enterprise Tier Users)

<br>Endpoint for create temporary-link to binary image.

<br>Required data:
- seconds_to_expire - Seconds to expire temporary link. Please type seconds between 300 - 30000
- image_id - ID of image 

## Technologies Used
- Django
- Django Rest Framework
- Docker
- Postgres

## How to run:
- Before first run:
```
docker-compose build
```
- Then, you have to add starter pack of tiers (Basic, Premium, Enterprise). To do this please run command:
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
