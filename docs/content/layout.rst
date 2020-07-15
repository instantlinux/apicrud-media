Project Layout
==============

This repository provides the layout for a typical Dockerized microservice. Here's what you'll find here, and you can browse the source code online `here <https://github.com/instantlinux/apicrud-media>`_.

.. code-block::

    root
    ├── aws-cors.xml             # Policy descriptions for storage
    ├── aws-s3-policy.json
    ├── b2-cors.json.json
    ├── media
    │   ├── celeryconfig.py      # celery-worker parameters
    │   ├── config.py            # application settings
    │   ├── constants.py         # global constants
    │   ├── db_schema.py         # db initial seed/update functions
    │   ├── main.py              # top-level startup
    │   ├── models               # models for database schema
    │   ├── openapi.yaml         # OpenAPI 3.0 specifications
    │   ├── rbac.yaml            # endpoint permissions
    │   ├── _version.py          # application version
    │   └── controllers          # controller classes
    │       ├── __init__.py      # controller initialization
    │       ├── album.py
    │       ├── auth.py
    │       ├── file.py
    │       ├── health.py
    │       ├── picture.py
    │       └── storage.py
    ├── docs                     # documentation directory
    ├── Dockerfile.media         # container image builder scripts
    ├── Dockerfile.media-worker
    ├── entrypoint-worker.sh     # container startup script
    ├── .github
    │   └── PULL_REQUEST_TEMPLATE.md  # template for code submission
    ├── .gitlab-ci.yml           # CI pipeline definition
    ├── Makefile                 # administrative utilities
    ├── .readthedocs.yml         # doc configuration
    ├── requirements.txt         # python dependencies
    ├── CONTRIBUTING.md
    ├── LICENSE.txt
    ├── README.md
    └── tests
        ├── conftest.py          # pytest settings
        ├── requirements.txt     # python test dependencies
        ├── test_base.py         # base class for writing tests
        └── test_xxx.py          # various tests
