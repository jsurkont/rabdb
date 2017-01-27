.PHONY: static

help:
	@:

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf app/production/static

clean-lib:
	rm -rf lib

pull-lib: clean-lib
	mkdir -p lib/superfamily
	wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.6.0/ncbi-blast-2.6.0+-x64-linux.tar.gz -P lib
	tar -xzf lib/ncbi-blast-*.tar.gz -C lib
	mv lib/ncbi-blast*/bin/blastp lib
	rm -rf lib/ncbi-blast*
	wget http://eddylab.org/software/hmmer3/3.1b2/hmmer-3.1b2-linux-intel-x86_64.tar.gz -P lib
	tar -xzf lib/hmmer-3*.tar.gz -C lib
	mv lib/hmmer-3*/binaries/hmmbuild lib
	mv lib/hmmer-3*/binaries/hmmpress lib
	mv lib/hmmer-3*/binaries/hmmscan lib
	mv lib/hmmer-3*/binaries/phmmer lib
	rm -rf lib/hmmer-3*
	wget --http-user ${SUPERFAMILY_USER} --http-password ${SUPERFAMILY_PWD} -r -np -nd -e robots=off \
	 -R 'index.html*' -P lib/superfamily 'http://supfam.org/SUPERFAMILY/downloads/license/supfam-local-1.75/'
	wget http://scop.mrc-lmb.cam.ac.uk/scop/parse/dir.cla.scop.txt_1.75 -O lib/superfamily/dir.cla.scop.txt
	wget http://scop.mrc-lmb.cam.ac.uk/scop/parse/dir.des.scop.txt_1.75 -O lib/superfamily/dir.des.scop.txt
	wget http://meme-suite.org/meme-software/4.11.2/meme_4.11.2_2.tar.gz -P lib

build-static:
	./app/manage.py collectstatic --noinput

build-docker-service: clean build-static
	docker build -t jsurkont/rabdb-service -f Dockerfile.service .

build-docker-worker: clean
	docker build -t jsurkont/rabdb-worker -f Dockerfile.worker .

check-production:
	cd app; ./manage.py check --deploy --settings=rabdb.settings_production

start: build-static
	uwsgi --http :9090 --chdir app --wsgi-file rabdb/wsgi.py --master \
		--processes 4 --threads 2 --check-static production

start-dev:
	./app/manage.py runserver
