## General information:

Django REST Framework API that allows any user to upload an image in PNG or JPG format:

- users can upload images via HTTP request
- users can list their images
- there are three bultin account tiers: Basic, Premium and Enterprise:
* users that have "Basic" plan after uploading an image get: 
- a link to a thumbnail that's 200px in height 
* users that have "Premium" plan get:
- a link to a thumbnail that's 200px in height
- a link to a thumbnail that's 400px in height
- a link to the originally uploaded image
* users that have "Enterprise" plan get:
- a link to a thumbnail that's 200px in height
- a link to a thumbnail that's 400px in height
- a link to the originally uploaded image
- ability to fetch a link to the (binary) image that expires after a number of seconds (user can specify any number between 300 and 30000)
* apart from the builtin tiers, admins can create arbitrary tiers with the following things configurable:
- arbitrary thumbnail sizes
- presence of the link to the originally uploaded file
- ability to generate expiring links



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
