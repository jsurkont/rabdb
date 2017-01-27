RabDB
=====

A web service for exploring the universe of Rab GTPases.

RabDB setup
-----------

RabDB setup is based on a web server, that hosts the RabDB website and the RabbitMQ message broker, and one or more rabifier workers that run the Rab predictions requested by the website.

Prepare host
^^^^^^^^^^^^

In this manual we create two virtual machines using KVM that run Ubuntu Server 14.04.

#. Install KVM ::

    sudo apt-get install qemu-kvm libvirt-bin bridge-utils

#. To use GUI install also ``virt-manager`` and ``qemu-system``

rabdb
^^^^^

#. Create a virtual machine with the ``rab`` user (default password: 12345)
#. Setup a database server e.g. PostgreSQL. ::

    apt-get install libpq-dev postgresql postgresql-contrib
    su - postgres
    psql


    CREATE DATABASE rabdb;
    CREATE USER rabdbuser WITH PASSWORD 'password';
    ALTER ROLE rabdbuser SET client_encoding TO 'utf8';
    ALTER ROLE rabdbuser SET default_transaction_isolation TO 'read committed';
    ALTER ROLE rabdbuser SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE rabdb TO rabdbuser;
    \q

    exit

#. Install ``rabbitmq-server`` and set it up ::

    apt-get install rabbitmq-server
    rabbitmqctl add_user rabifier mypassword
    rabbitmqctl add_vhost rabdb-vhost
    rabbitmqctl set_permissions -p rabdb-vhost rabifier ".*" ".*" ".*"

#. Install and configure Apache ::

    apt-get install libapache2-mod-wsgi  # NOTE: install libapache2-mod-wsgi-py3 for Python3 support
    a2enmod wsgi  # activate the module

    ### OPTIONAL ###
    # Test wsgi by creating a file var/www/wsgi_app.py with the following contents:
    def application(environ, start_response):
        status = '200 OK'
        output = b'Hello world, I am a wsgi app!'
        response_headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

    # Make a temporary entry in the apache configuration file for testing wsgi somewhere at the end of /etc/apache2/apache2.conf:
    ServerName TestWsgi
    WSGIScriptAlias /wsgi /var/www/wsgi_app.py

    # Restart the server
    service apache2 restart

    # Point the browser to 127.0.0.1/wsgi and you should be greeted with:
    Hello world, I am a wsgi app!
    ### END OPTIONAL ###

#. Create a Python virtual environment ::

    apt-get install python-virtualenv python-dev
    cd $HOME
    virtualenv venv

#. Install ``rabifier``, note that you don't need to install any third-party software required by ``rabifier``,
   except for the Python modules, unless you want to run ``rabifier`` from the same machine as the web server
   (``scipy``, a rabifier's dependency, requires some system libraries to compile, install: gfortran,
   libblas-dev, liblapack-dev) ::

    pip install rabifier

#. Change permissions to allow Apache to read the files in ``/home/rab/venv/lib/python2.7/site-packages`` ::

    chgrp -R www-data venv/lib/python2.7/site-packages/

#. Clone the ``rabdb`` repository to ``$HOME``, install its dependencies. Modify ``manage.py``: change
   ``rabdb.settings`` to ``rabdb.settings_production``
#. Update ``rabdb/rabdb/settings_production.py`` with the correct PostgreSQL and  RabbitMQ information.
#. Create database tables ::

    ./manage migrate

#. Populate the database using ``./manage.py populatedb`` and precomputed predictions, check ``./manage.py help populatedb``
   for more information. This command uses NCBI Taxonomy that needs to be downloaded and preprocessed at the first usage.
   This process requires ~3GB of memory, you can either temporally expand the VM's memory or pre-compute the Taxonomy DB
   on a different machine and copy it to ``~/.etetoolkit``, check ``ete2`` documentation for more information. Note,
   ``populatedb`` only uses positive Rab predictions, so it's better to run ``rabifier`` with the ``--show_positive`` option.
   Apache restart may be required for changes to appear on the website.

#. Collect static files ::

    ./manage.py collectstatic

#. Ensure that apache is able to read files in the project ::

    chgrp -R www-data rabdb
    find rabdb -type d -exec chmod g+rwx {} +
    find rabdb -type f -exec chmod g+r {} +

#. Configure Apache to work with RabDB ::

    cp rabdb/production/config/rabdb.conf /etc/apache2/sites-available/rabdb.conf
    chmod 644 /etc/apache2/sites-available/rabdb.conf
    a2ensite rabdb
    a2dissite 000-default
    service apache2 restart

rabdb-worker
^^^^^^^^^^^^

#. Create a virtual machine with the ``rabdbworker`` user (default password: 12345)
#. Create a Python virtual environment ::

    cd $HOME
    virtualenv virtualenv

#. Install ``rabifier`` (``scipy``, a rabifier's dependency, requires some system libraries to compile, install them) ::

    pip install rabifier

#. Ensure that rabifier dependencies are present (check rabifier's docs) and available in the system path for
   all users e.g. add ``/home/rabdbworker/system/bin`` to ``/etc/environment``.
#. Clone the ``rabdb`` repository to ``$HOME``, install its dependencies.
#. Configure rabdb.
    #. Select the appropriate settings file in ``rabdb/celery.py``, e.g. the rabdb settings file.
    #. Point RabbitMQ to the correct server.
    #. Update the email settings.
    #. Make sure that the connection to the database can be established or a local dummy sqlite is set (otherwise celeryd fails to load).
#. Add daemon scripts to the system ::

    cp production/config/celeryd.conf  /etc/default/celeryd
    cp production/config/celeryd.init  /etc/init.d/celeryd
    chmod 644 /etc/default/celeryd
    chmod 755 /etc/init.d/celeryd
    service celeryd start

#. Run celery daemon at the boot time. Use e.g. ``rcconf`` to configure it (may require a reboot if ``celeryd`` doesn't show up in the list).
