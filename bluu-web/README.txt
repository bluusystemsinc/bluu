Installation procedure:

1. python bootstrap.py --distribute

2. bin/buildout -c devel.cfg

3. create database (default db is sqlite; sqlite db is created automatically by Django). We do recommend Postgres SQL. Database settings like: user, password, dbname should be adjusted at: project/production.py (or test.py for test environment, or development.py for development environment)

4. run:
   bin/django syncdb
   bin/django migrate

5. run:
   bin/django runscript initialize_roles

6. start application:
   bin/django runserver

7. to run system in production environment omit step 6. instead configure web server to run Django. For more information about this look into Django docs.

Explanation:
1. Project uses buildout (buildout.org) to perform installation
2. Base buildout configuration is at buildout.cfg
3. Depending on environment we're going to run the project in, we have: devel.cfg, test.cfg production.cfg.
   These configuration files extend buildout.org for example to force Django to use different settings files in specific environments.
4. In the "project" folder we have settings file: settings.py and specific settings files for different environments: development.py, test.py i production.py
5. >>> bin/django command is almost equal to >>> python manage.py The difference is that bin/django knows all paths for additional modules

