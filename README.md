# RabDB

A web service for exploring the universe of Rab GTPases.

## Usage

RabDB requires an SQL database (tested with SQLite and PostgreSQL) and a
message broker to distribute Rab prediction tasks (tested with RabbitMQ as a
broker and Redis a result backend).

### Development

1. Install Python dependencies `pip install -r requirements.txt`
2. Create the database structure `./app/manage.py migrate`
3. (optional) Populate the database with Rab predictions, see
`./app/manage.py populatedb --help` for more details.
4. Run the server `./app/manage.py runserver`

### Production

Probably the easiest method to deploy RabDB into production uses docker images.

1. Create images

  ```bash
  make build-docker-service
  make build-docker-worker
  ```

2. Run images

  ```bash
  # Run the service
  docker run -d --name rabdb-service \
    -e RABDB_DATABASE=$(RABDB_DATABASE) \
    -e RABDB_BROKER=$(RABDB_BROKER) \
    -e RABDB_RESULT_BACKEND=$(RABDB_RESULT_BACKEND) \
    -p 3031:3031 \
    jsurkont/rabdb-service

  # Run the result maintenance worker
  docker run -d --name rabdb-service-beat \
    -e RABDB_BROKER=$(RABDB_BROKER) \
    -e RABDB_RESULT_BACKEND=$(RABDB_RESULT_BACKEND) \
    jsurkont/rabdb-service celery -A rabdb beat

  # Run the Rab prediction worker
  # NOTE: you can run multiple instances of rabdb-woker on different machines
  # to distribute jobs
  docker run -d --name rabdb-worker \
    -e RABDB_BROKER=$(RABDB_BROKER) \
    -e RABDB_RESULT_BACKEND=$(RABDB_RESULT_BACKEND) \
    jsurkont/rabdb-worker
  ```

Ensure that the database exists and contains Rab predictions, see
`./app/manage.py populatedb --help` for more details.
