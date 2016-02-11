help:
	@:

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} +

check-production:
	./manage.py check --deploy --settings=rabdb.settings_production
