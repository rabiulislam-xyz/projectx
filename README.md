# Custom boilerplate for Django/DRF

## Used technologies
Django, DRF, Postgres, Docker, Redis

---
## Project setup
- clone this repository and cd into it
- run `docker-compose up -d --build` project will be running on `localhost:8000`
- migrate `docker exec app python manage.py migrate`
- seed dummy data `docker exec app python manage.py loaddata dump.json`
- run tests `docker exec app python manage.py test`

---
## API endpoints
| Endpoint                                | Description                   |
|-----------------------------------------|-------------------------------|
| http://localhost:8000/api/v1/docs/      | API Documentation             |
| http://localhost:8000/api/v1/token/     | Login/Token Generation        |
| http://localhost:8000/api/v1/users/     | Users CRUD endpoint           |

---
## Credentials
admin username: `admin`
admin password: `admin`
