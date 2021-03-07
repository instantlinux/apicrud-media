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
    │   ├── config.yaml          # application settings
    │   ├── constants.py         # global constants
    │   ├── main.py              # top-level startup
    │   ├── models
    │   │   ├── __init__.py      # models for database schema
    │   │   ├── api.py           # open-core API models
    │   │   ├── base.py          # declarative base
    │   │   └── media.py         # open-core media models
    │   ├── models               # models for database schema
    │   ├── openapi              # OpenAPI 3.0 specifications
    │   │   ├── api.yaml         # top-level API spec
    │   │   ├── album.schema.yaml  # open-core API model schema
    │   │   ├── album.path.yaml    # open-core API routing paths
    │   │   └── ...              # add your custom specs here
    │   ├── rbac.yaml            # endpoint permissions
    │   ├── _version.py          # application version
    │   └── controllers          # controller classes
    │       ├── __init__.py      # controller initialization
    │       ├── album.py
    │       ├── auth.py
    │       ├── file.py
    │       ├── health.py
    │       ├── metrics.py
    │       ├── picture.py
    │       └── storage.py
    ├── docs                     # documentation directory
    ├── Dockerfile.media         # container image builder scripts
    ├── Dockerfile.media-worker
    ├── entrypoint-worker.sh     # container startup script
    ├── .github
    │   └── PULL_REQUEST_TEMPLATE.md  # template for code submission
    ├── .gitlab-ci.yml           # CI pipeline definition
    ├── i18n                     # application language translations
    │   ├── messages.pot         # extracted language strings
    │   ├── ar                   # arabic message mappings
    │   └── de (...)             # german messages (and so on)
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
