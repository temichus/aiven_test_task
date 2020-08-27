# Aiven Test automation developer homework
This README document contains short task description and Documentation regarding proposed solution
## Exercise:
Exercise
Your task is to implement a system that monitors website availability over the network, produces metrics about this and passes these events through an Aiven Kafka instance into an Aiven PostgreSQL database.

For this, you need a Kafka producer which periodically checks the target websites and sends the check results to a Kafka topic, and a Kafka consumer storing the data to an Aiven PostgreSQL database. For practical reasons, these components may run in the same machine (or container or whatever system you choose), but in production use similar components would run in different systems.
The website checker should perform the checks periodically and collect the HTTP response time, error code returned, as well as optionally checking the returned page contents for a regexp pattern that is expected to be found on the page.

For the database writer we expect to see a solution that records the check results into one or more database tables and could handle a reasonable amount of checks performed over a longer period of time.
Please pay attention to  having a good set of tests. For simplicity your tests can assume Kafka and PostgreSQL services are already running, instead of integrating Aiven service creation and deleting.
Aiven is a Database as a Service vendor and the homework requires using our services. Please register to Aiven at https://console.aiven.io/signup.html at which point you'll automatically be given $300 worth of credits to play around with. The credits should be enough for a few hours of use of our services. If you need more credits to complete your homework, please contact us.
The solution should NOT include using any of the following:

Database ORM libraries - use a Python DB API compliant library and raw SQL queries instead
Extensive container build recipes - rather focus your effort on the Python code, tests, documentation, etc.
Criteria for evaluation

Code formatting and clarity. We value readable code written for other developers, not for a tutorial, or as one-off hack.
We appreciate demonstrating your experience and knowledge, but also utilizing existing libraries. There is no need to re-invent the wheel.
Practicality of testing. 100% test coverage may not be practical, and also having 100% coverage but no validation is not very useful.
Automation. We like having things work automatically, instead of multi-step instructions to run misc commands to set up things. Similarly, CI is a relevant thing for automation.
Attribution. If you take code from Google results, examples etc., add attributions. We all know new things are often written based on search results.
## Solution
### Requirements
The minimal python version is 3.7

### Installation
To install the required packages, download GitHub project and execute the following command in the root project's directory:
```
pip3 install -r requirements.txt
```
### Configuration
Solution has 3 configs in yaml format:

* producer_config.yaml - data for website checker
* consumer_config.yaml - data for db writer
* kafka_config.yaml - common data for Kafka consumer/poroducer clients

As example, these configs are already filled to use local and Aiven Dev Test Enviroment

#### producer_config.yaml

```
#set delay to configure checks periodicity
delay_between_checks: <INT>

#set list of URLs to check:
websites_to_check:
  - url: <URL 1>
  - url: <URL 2>
     regex: "<REGULAR EXPRESSION>" # optional param
```

#### consumer_config.yaml

```
sql_credentials:
  #DSN for DB connection
  dsn: 'SOME DSN'
  #(optional) CA file path for DB. None by dafault
  ca_file : "pg_ca.pem"
  # (optional) Should the BD been wiped ad start. False by default
  wipe_db : true
 ```

#### kafka_config.yaml

```
kafka_config:
  # kafka bootstrap servers
  bootstrap_servers: 'kafka-ccf8234-temichus-3df1.aivencloud.com:24383'
  # kafka topoc
  topic: 'websites_monitor'

  # (optional) data to setup ssl context
  ssl_context:
    # CA used to sign certificate file
    cafile: "ca.pem"
    # Signed certificate file
    certfile: "service.cert"
    # Private Key file of `certfile` certificate
    keyfile: "service.key"
 ```


### Execution
there are 2 execution options

1. start everything in one process
```
python same_machine_main.py
```
2. Start 2 independent processes in different systems
```
python consumer_main.py
```

```
python producer_main.py
```

### Run tests
#### Installation requirements for tests
```
pip3 install -r tests/requirements.txt
```
#### Execution
```
pytest /tests
```
#### Tests coverage
For calculating coverage Coverage.py tool was used
```
coverage run -m pytest tests/ && coverage report --omit "tests*"
```
Last coverage result:

|Stmts|Miss|Cover|
|---  |--- |---  |
|231  |14  |94%  |
### Attribution
* https://docs.aiohttp.org/en/stable/
* https://aiokafka.readthedocs.io/en/stable/
* https://magicstack.github.io/asyncpg/current/index.html
* https://pypi.org/project/pytest-mock/
* https://pypi.org/project/asyncmock/
## TODO/ Possible Improvements
* Use table partitioning to store huge data in 'monitor.signal_data' PostgreSQL table
* Improve solution to work with batch of messages instead of sending/receiving to/from Kafka and inserting in DB 1 by 1