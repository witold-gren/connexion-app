# Documentation

This documentation cover decision and ideas to create API app. Also here you will find commands on how to run the 
application. It was divided into 4 sections:
- [Application](#application)
- [Docker](#docker)
- [Kubernetes](#kubernetes) 
- [CI/CD](##continuous-integration)

## Application

### Locally requirements:
- git 
- docker
- docker-compose

Before you start working please download all configuration from git repository:

    git clone https://github.com/witold-gren/connexion-app.git connexion-app

Be sure that you have "docker" and "docker-compose" installed. Then you need to enter the root directory: 

    cd connexion-app

All what you have to do is run one command:

    docker-compose up

Wait a couple of minutes when docker download postgresql and python images. Docker will also build and prepare all necessary data.


Import data
-----------

During migration application also imports data into the database from the supplied csv file.
However, you can import additional data yourself from another csv file.

    docker-compose run --rm app flask import_data my_data.csv


Settings variables
------------------

| Variables name        | Description                                        |
|-----------------------|----------------------------------------------------|
| FLASK_DEBUG           | enables application debug mode                     |
| FLASK_APP             | determines how flask should launch the application |
| CHECK_MIGRATION       | check migrations before launching the container    |
| POSTGRES_HOSTNAME     | database host                                      |
| POSTGRES_PORT         | database port                                      |
| POSTGRES_DB           | database name                                      |
| POSTGRES_USER         | database user                                      |
| POSTGRES_PASSWORD     | database password                                  |

Extra production settings
-------------------------

| Variables name          | Description                                                                                         |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| APP_SETTINGS            | setting the environment in which we run the application (development, testing, staging, production) |
| GUNICORN_HOST           | setting the host address                                                                            |
| GUNICORN_PORT           | setting the application port                                                                        |
| GUNICORN_TIMEOUT        | timeout setting for request                                                                         |
| GUNICORN_WORKERS        | setting the number of starting gunicorn process                                                     |
| GUNICORN_WORKER_CLASS   | setting the class how gunicorn will process requests                                                |
| GUNICORN_ACCESS_LOGFILE | set access to the log file                                                                          |
| GUNICORN_ERROR_LOGFILE  | error file access setting                                                                           |


### Explanation
I know Django very well but for first time I am writing an application in the Flask framework. I decided choose flask 
because this api is very small. We didn't need a large and extensive tool. I also was focused to create small image 
with python app (it is not very easy). That is the reason why I didn't install extra useful python libraries. 

I used the `connexion` library to build the api. This library with very little effort reflects the api. API must be 
described in yaml format using swagger. The library automatically builds endpoints and validates the sent data 
according to the defined file.

`Flask-SQLAlchemy` (`SQLAlchemy`, `psycopg2`) and `Flask-Migration` (`Alembic`) were used for communication with database.
`Gunicorn` was used to launch the application in the kubernetes cluster. The `coverage` module was used to generate 
a code coverage report. The `environs` module is used to download environment variables and convert to python objects. 
`Flask-Testing` with standard `unittest` module were usade for testing application. 

Other modules not installed but very useful
-------------------------------------------
- pytest, pytest-cov, pytest-xdist, pytest-sugar, pytest-faker, pytest-mock, pytest-factoryboy (framework for simple test writing)
- marshmallow (library for serializing complex python objects to json) 
- factory-boy (factory of objects based on defined database models)
- argon2-cffi (very strong password hashing library)
- healthcheck (library which provide health check endpoint for app)
- flask-prometheus-metrics (prometheus metrics exporter for Flask web applications)
- sphinx (tool for create documentation)
- pudb (python debugger)
- isort, pylama, pylama-pylint,radon, black (tools for auditing code)

Todo for future
---------------
To make the application work safer and more efficiently, it's worth creating a pagination of the list of people. 
This option wasn't added to api description. This is the reason why this has not been implemented.

## Docker

Dockerfile
----------

Dockerfile contains best image building practices:
- contains the minimum number of layers
- contains multi-steps to delete unneeded libraries
- contains extra user to don't run applications with root privileges
- contains minimal numbers of layer
- contains "cache layer" (proper arrangement) not to build the container from the first layer
- contains the smallest python image

Entrypoint
----------
Entrypoint includes 3 additional configurations. 
- The first always checks if there is a database connection. If there is no connection, the application will not start. 
- The second one checks if database migration has been applied and if data has been imported from a csv file. 
  This migration is only performed on the local environment (debug mode is true) and only during the first container creation.
- The third configuration checks whether all available migrations and imports have already been applied. 
  This configuration is only used on the kubernetes cluster and is not started locally.

Also, three additional commands have been created:
- migrate (hem run migration by hand, it is used in kubernetes job)
- test (help run test locally)
- cov (help run code coverage locally)

Test your code:

    $ docker-compose run --rm app test

    Starting db ... done
    PostgreSQL is up - continuing...
    Initial db
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.
    .http://localhost/people validation error: '20' is not of type 'integer' - 'age'
    .http://localhost/people validation error: '20' is not of type 'number' - 'fare'
    ..http://localhost/people validation error: '20' is not of type 'integer' - 'parentsOrChildrenAboard'
    .http://localhost/people validation error: '20' is not of type 'integer' - 'passengerClass'
    .http://localhost/people validation error: '20' is not one of ['male', 'female', 'other'] - 'sex'
    .http://localhost/people validation error: '20' is not of type 'integer' - 'siblingsOrSpousesAboard'
    .http://localhost/people validation error: 1 is not of type 'boolean' - 'survived'
    .http://localhost/people validation error: 1 is not of type 'string' - 'name'
    .................................................
    ----------------------------------------------------------------------
    Ran 58 tests in 5.485s
    
    OK


Test code coverage:

    $ docker-compose run --rm app cov
    
    Starting db ... done
    PostgreSQL is up - continuing...
    Initial db
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.
    Name                   Stmts   Miss  Cover
    ------------------------------------------
    api/__init__.py            0      0   100%
    api/people.py              8      0   100%
    api/person.py             13      0   100%
    app.py                    49     10    80%
    commands.py               62     37    40%
    config.py                 25      0   100%
    extensions.py             35     11    69%
    models/__init__.py         1      0   100%
    models/person.py         114      1    99%
    tests/__init__.py          0      0   100%
    tests/test_api.py        196      1    99%
    tests/test_models.py     181      1    99%
    wsgi.py                    6      6     0%
    ------------------------------------------
    TOTAL                    690     67    90%

Run your migration usage extra command (eg. job object usage this command for tun migration):

    $ docker-compose run --rm app migrate
    
    Starting db ... done
    PostgreSQL is up - continuing...
    Initial db
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.

The file `start.sh` is used for local container launch. It runs one threaded application and automatically reloads python code.
The file `gunicorn.sh` is used for kubernetes environments. It contains default production configuration with default variables.

## Kubernetes

Kubernetes configuration contains two way to deploy our app. First way is use clean kubectl tool with simple yaml file. 
Second way use `kustomize` with configuration contains three environments. This configuration is quite sample and 
didn't need extra operators. But in real environment better way is use eg. for secrets AWS SSM Parameter Store (aws-ssm operator)
or Hashicorp Vault (vault-k8s). But it is impossible to prepare one line command to provision and configure everything :)  

### Kubectl 

Before you start, you must change your domain in ingress object `application/ingress.yaml`. Current domain 
is `app.example.com` but this is only example. In real environment this domain will by always the same, 
or if you use several environments to provision this app best way is start use `helm` or `kustomize` (see below).

If you need usage one command to run this environment in kubernetes you mas usage this:

    $ kubectl apply -R -f kubernetes/kubectl/
    
    namespace/development created
    configmap/connexion-app-configmap created
    deployment.extensions/connexion-app-deploy created
    horizontalpodautoscaler.autoscaling/connexion-app-hpa created
    ingress.extensions/connexion-app-ingress created
    job.batch/connexion-app-job created
    secret/connexion-app-secret created
    service/connexion-app-svc created
    configmap/postgresql-configmap created
    secret/postgresql-secret created
    service/postgresql-svc created
    statefulset.apps/postgresql created


Or if you need more control to run this application, try this steps:

Create new namespace for you environment:

    kubectl apply -f kubernetes/kubectl/app-namespace.yaml

Deploy database:

    kubectl apply -f kubernetes/kubectl/postgres/

Deploy flask application:

    kubectl apply -f kubernetes/kubectl/application/

### Kustomize

Also if we need manage more environments we are able usage `kustomize`. It is also usage to deploy our application by Jenkins. 
Before we start deploy one of environments we must update ingress host. Check folder `kubernetes/kustomize/application/overlays` 
with files `development/ingress.yaml`, `staging/ingress.yaml` and `production/ingress.yaml` and update host addresses.

To deploy our app, first we must deploy data base and next our app selecting environment. For example if we need staging
environment, we must use:

    $ kubectl apply -k kubernetes/kustomize/postgres/overlays/staging
    ..
    $ kubectl apply -k kubernetes/kustomize/application/overlays/staging
 
`Kustomize` is used for Jenkins for deploy our app in selected environment.

### Explanation

The current configuration includes creating only one environment. 
The current configuration will work because it downloads an image from my public repository with the application.
To use another repository, build and push a new docker image and change the files accordingly 
`application/deployment.yaml`, `application/job.yaml` and/or `postgres/statefulset.yaml` in `kubectl` folder or 
you must update similar file in `kustomize` folder if you prefer use `kustomize`.

The job object was used to migrate data. This object is launched only one time, no matter how many application containers we have.
Applications will not run until migrations are complete. During deployment, three containers are launched in different Availability Zones.

## Continuous Integration

For continuous integration and continuous deployment we usage two files. The first is Jeninsfile. It is usage in app repository
to build, test and upload our image to docker hub. (To start use this pipeline we must configure Jenkins Job and few configuration).
This example don't provide base ready jenkins image to deploy our app. The second file is Jenkinsfile_deploy which should by
added to repository when we have kubernetes configuration with yaml files. 


# Small mistakes found:
- bad http code in swagger file
- small mistakes with data in csv file
