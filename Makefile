.PHONY: static

help:
	@:

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} +

build-static:
	./manage.py collectstatic

check-production:
	./manage.py check --deploy --settings=rabdb.settings_production

start:
	uwsgi --http :9090 --wsgi-file rabdb/wsgi.py --master --processes 4 --threads 2 --check-static production

start-dev:
	./manage.py runserver
