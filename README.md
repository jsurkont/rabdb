# RabDB

A web service for exploring the universe of Rab GTPases. For more information
see:

* Rabifier2: an improved bioinformatic classifier of Rab GTPases.
  Surkont J, *et al.* (2016) Bioinformatics [doi:10.1093/bioinformatics/btw654](http://bioinformatics.oxfordjournals.org/content/early/2016/10/20/bioinformatics.btw654.abstract)
* Thousands of Rab GTPases for the Cell Biologist.
  Diekmann Y, *et al.* (2011) PLoS Comput Biol 7(10): e1002217
  [doi:10.1371/journal.pcbi.1002217](http://dx.plos.org/10.1371/journal.pcbi.1002217)

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
  make pull-lib
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
