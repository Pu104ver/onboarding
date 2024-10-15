### Django Project with Docker

This project is a Django application containerized with Docker. The following instructions will guide you through setting up, running, and managing the project using Docker and Docker Compose.

## Prerequisites

Make sure you have the following installed on your local machine:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Project Setup

### Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://your-repo-url.git
cd your-repo-directory
```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables. For ex:

```env
POSTGRES_DB=onboarding
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_HOST=db
POSTGRES_PORT=5432

DEBUG=True

SECRET_KEY=django-insecure-g3==_4_6cagmn5v3cuc$=wjby!f-#4zh$)6qi+($0&yc$4t&=s

ALLOWED_HOSTS="0.0.0.0"
```

### Docker Compose

The `docker-compose.yml` file defines the services for this project:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    container_name: postgres
    env_file:
      - .env
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: daphne -b 0.0.0.0 -p 8000 onboarding.asgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - .env
    restart: always

volumes:
  postgres_data:
```

### Dockerfile

The `Dockerfile` specifies how the web service container is built:

```Dockerfile
FROM python:3.12

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "onboarding.asgi:application"]
```

## Running the Application

### Build and Start the Containers

To build and start the containers, run:

```bash
docker-compose up --build -d
```

This will build the Docker images and start the containers in detached mode.

### Apply Migrations

After the containers are up, you need to apply the migrations to set up the database schema:

```bash
docker-compose exec web python manage.py migrate
```

### Create a Superuser

To create a superuser for accessing the Django admin interface, run:

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to set up the superuser account.

### Access the Application

Once everything is set up, you can access

- the application at `http://localhost:8000`
- the Django admin interface at `http://localhost:8000/admin`.
- the API at http://127.0.0.1:8000/api/swagger/

## Stopping the Application

To stop the running containers, use:

```bash
docker-compose down
```

This will stop and remove the containers, networks, and volumes defined in the `docker-compose.yml` file.

## Additional Commands

### Viewing Logs

To view the logs of the running containers:

```bash
docker-compose logs
```

### Rebuilding the Containers

If you make changes to the `Dockerfile` or `docker-compose.yml`, you can rebuild the containers using:

```bash
docker-compose up --build -d
```

### Running Management Commands

You can run any Django management command in the web container using `docker-compose exec`:

```bash
docker-compose exec web python manage.py <command>
```

## Troubleshooting

If you encounter any issues, check th logs using `docker-compose logs` and ensure that all environment variables are correctly set in the `.env` file.

---

This README should provide a comprehensive guide to setting up and running your Django application using Docker. If you have any questions or need further assistance, feel free to ask.

```

This README provides a detailed step-by-step guide for setting up, running, and managing your Django application using Docker, along with applying migrations and creating a superuser. It should be useful for both new and experienced developers.
```
