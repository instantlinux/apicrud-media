# Usage:
# See .gitlab-ci.yml for the main pipeline

MAXFAIL    ?= 1000
PYPI_URL   ?= https://upload.pypi.org/legacy/
PYPI_USER  ?= $(USER)
VERSION    ?= $(shell grep -o '[0-9.]*' media/_version.py)
export REGISTRY    ?= $(REGISTRY_URI)/$(CI_PROJECT_PATH)
export APP_ENV ?= local

include Makefile.vars
include Makefile.i18n

# Local dev

run_media: py_requirements
	. $(VDIR)/bin/activate && \
	  AMQ_HOST=$(RABBITMQ_IP) REDIS_HOST=$(REDIS_IP) \
	  PUBLIC_URL=http://$(FQDN):$(APP_PORT) \
	  FLASK_ENV=development PYTHONPATH=media python3 -m media.main

media_worker:
	. $(VDIR)/bin/activate &&  \
	  AMQ_HOST=$(RABBITMQ_IP) REDIS_HOST=$(REDIS_IP) \
	  PYTHONPATH=media \
	  celery -A media_worker worker -Q media_$(APP_ENV) \
	  -n media1@%h --loglevel=INFO

VENV=python_env
VDIR=$(PWD)/$(VENV)

.PHONY: qemu

analysis: flake8

test_functional:
	@echo "Run Functional Tests - not yet implemented"

python_env: $(VDIR)/bin/python3

$(VDIR)/bin/python3:
	@echo "Creating virtual environment"
	python3 -m venv --system-site-packages $(VENV)

media/openapi.yaml: $(wildcard media/openapi/*.yaml)
	@echo "Generating openapi.yaml"
	. $(VDIR)/bin/activate && dref media/openapi/api.yaml $@

flake8: test_requirements
	@echo "Running flake8 code analysis"
	. $(VDIR)/bin/activate && flake8 media tests

# for the create_image rule, do this instead for openapi.yaml
openapi_deploy:
	pip install dollar-ref
	ls -l $(find . -name dref)
	/build/.local/bin/dref media/openapi/api.yaml media/openapi.yaml
	chmod 644 media/openapi.yaml

$(VDIR)/lib/python3.6/site-packages/pytest.py: python_env
	@echo "Installing test requirements"
	(. $(VDIR)/bin/activate && pip3 freeze && \
	 pip3 install -r tests/requirements.txt)
$(VDIR)/lib/python3.6/site-packages/flask/app.py: python_env
	@echo "Installing main requirements"
	(. $(VDIR)/bin/activate && \
	 pip3 install -r requirements.txt)
py_requirements: $(VDIR)/lib/python3.6/site-packages/flask/app.py
test_requirements: $(VDIR)/lib/python3.6/site-packages/pytest.py

test: test_requirements py_requirements media/.proto.sqlite \
	    media/i18n/en/LC_MESSAGES/messages.mo media/openapi.yaml
	@echo "Running pytest unit tests"
	cd media && \
	(. $(VDIR)/bin/activate && \
	 DB_SEED_FILE=$(PWD)/tests/db_fixture.yaml \
	 PYTHONPATH=. python3 -m pytest $(XARGS) ../tests \
	 --maxfail=$(MAXFAIL) \
	 --durations=10 \
	 --junitxml=../tests/results.xml \
	 --cov-report html \
	 --cov-report xml \
	 --cov-report term-missing \
	 --cov ../python_env/lib/python*/site-packages/apicrud/media \
	 --cov .)

media/.proto.sqlite:
	@echo Generating prototype sqlite db
	@echo **note** schema changes require a .schema dump from apicrud
	sqlite3 $@ < tests/schema-cac2000912a5.sql

media/i18n/en/LC_MESSAGES/messages.mo:
	make i18n_compile

clean:
	rm -rf build dist *.egg-info .cache .pytest_cache */__pycache__ \
	 */.coverage */.proto.sqlite */coverage.xml */htmlcov */results.xml \
	 docs/_build docs/content/stubs media/openapi.yaml
	find . -name '*.pyc' -or -name '*~' -exec rm -rf {} \;
wipe_clean: clean
	rm -rf python_env

create_image: qemu i18n_deploy openapi_deploy
	@echo docker build -t $(REGISTRY)/$(IMGNAME)-$(CI_JOB_NAME):$(TAG)
	@docker buildx build \
	 --tag $(REGISTRY)/$(IMGNAME)-$(CI_JOB_NAME):$(TAG) . \
	 --push -f Dockerfile.$(CI_JOB_NAME) \
	 --build-arg=VCS_REF=$(CI_COMMIT_SHA) \
	 --build-arg=TAG=$(TAG) \
	 --build-arg=BUILD_DATE=$(shell date +%Y-%m-%dT%H:%M:%SZ)

promote_images: qemu i18n_deploy openapi_deploy
ifeq ($(CI_COMMIT_TAG),)
	$(foreach target, $(IMAGES), \
	  image=$(shell basename $(target)) && \
	  docker buildx build --platform $(PLATFORMS) \
	    --tag $(REGISTRY)/$(IMGNAME)-$${image}:latest \
	    --push --file Dockerfile.$${image} . \
	    --build-arg=VCS_REF=$(CI_COMMIT_SHA) \
	    --build-arg=BUILD_DATE=$(shell date +%Y-%m-%dT%H:%M:%SZ) \
	;)
else
	# Push tagged items to two registries: REGISTRY is gitlab,
	# USER_LOGIN refers to docker hub
	docker login -u $(USER_LOGIN) -p $(DOCKER_TOKEN)
	$(foreach target, $(IMAGES), \
	  image=$(shell basename $(target)) && \
	  docker buildx build --platform $(PLATFORMS) \
	    --tag $(REGISTRY)/$(IMGNAME)-$${image}:$(CI_COMMIT_TAG) \
	    --tag $(REGISTRY)/$(IMGNAME)-$${image}:latest \
	    --tag $(USER_LOGIN)/$(IMGNAME)-$${image}:$(CI_COMMIT_TAG) \
	    --tag $(USER_LOGIN)/$(IMGNAME)-$${image}:latest \
	    --push --file Dockerfile.$${image} . \
	    --build-arg=VCS_REF=$(CI_COMMIT_SHA) \
	    --build-arg=BUILD_DATE=$(shell date +%Y-%m-%dT%H:%M:%SZ) \
	;)
	curl -X post https://hooks.microbadger.com/images/$(USER_LOGIN)/$(IMGNAME)-$${image}/$(MICROBADGER_TOKEN)
endif

clean_images:
	docker rmi $(REGISTRY)/$(IMGNAME)-api:$(TAG) || true
	docker rmi $(REGISTRY)/$(IMGNAME)-worker:$(TAG) || true

qemu:
	docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
	docker buildx create --name multibuild
	docker buildx use multibuild
