Installation procedure:

1. python bootstrap.py --distribute

2. bin/buildout -c devel.cfg

3. create database (default db is sqlite; sqlite db is created automatically by Django).
   We do recommend Postgres SQL. Database settings like: user, password, dbname should be
   adjusted at: project/production.py (or test.py for test environment, or development.py for development environment)

4. run:
   bin/django syncdb
   bin/django migrate

5. run:
   bin/django runscript initialize_roles

6. start application:
   bin/django runserver

7. to run system in production environment omit step 6.
   instead configure web server to run Django.
   For more information about this see Django docs (https://docs.djangoproject.com/en/1.5/howto/deployment/)

8. Set up cron jobs:
* *  * * * (/opt/webapps/test/bluu/bin/django send_mail >> /opt/webapps/test/cron_bluu_mailer.out 2>&1)
0,20,40 * * * * (/opt/webapps/test/bluu/bin/django retry_deferred >> /opt/webapps/test/cron_bluu_mailer.out 2>&1)
0 0 * * * (/opt/webapps/test/bluu/bin/django cleanupinvitation >> /opt/webapps/test/cron_bluu_invitations.out 2>&1)


Additional informations:
1. Project uses buildout (buildout.org) to perform installation
2. Base buildout configuration is at buildout.cfg
3. Depending on environment we're going to run the project in, we have: devel.cfg, test.cfg production.cfg.
   These configuration files extend buildout.cfg - that allows Django to use different settings files in specific environments.
4. In the "project" folder we have settings file: settings.py and specific settings files for different environments: development.py, test.py i production.py
5. >>> bin/django command is almost equal to >>> python manage.py command. The difference is that bin/django knows all paths for additional modules installed by buildout

