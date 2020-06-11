# Usage:
# See .gitlab-ci.yml for the main pipeline

MAXFAIL    ?= 1000
PYPI_URL   ?= https://upload.pypi.org/legacy/
PYPI_USER  ?= $(USER)
VERSION    ?= $(shell grep -o '[0-9.]*' media/_version.py)
export REGISTRY    ?= $(REGISTRY_URI)/$(CI_PROJECT_PATH)
export APP_ENV ?= local

include Makefile.vars

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

flake8: test_requirements
	@echo "Running flake8 code analysis"
	. $(VDIR)/bin/activate && flake8 media tests

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

test: test_requirements py_requirements media/.proto.sqlite
	@echo "Running pytest unit tests"
	cd media && \
	(. $(VDIR)/bin/activate && \
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
	sqlite3 $@ < tests/schema-cac2000912a5.sql

clean:
	rm -rf build dist *.egg-info .cache .pytest_cache */__pycache__ \
	 */.coverage */.proto.sqlite */coverage.xml */htmlcov */results.xml
	find . -name '*.pyc' -or -name '*~' -exec rm -rf {} \;
wipe_clean: clean
	rm -rf python_env

create_image: qemu
	@echo docker build -t $(REGISTRY)/$(IMGNAME)-$(CI_JOB_NAME):$(TAG)
	@docker buildx build \
	 --tag $(REGISTRY)/$(IMGNAME)-$(CI_JOB_NAME):$(TAG) . \
	 --push -f Dockerfile.$(CI_JOB_NAME) \
	 --build-arg=VCS_REF=$(CI_COMMIT_SHA) \
	 --build-arg=TAG=$(TAG) \
	 --build-arg=BUILD_DATE=$(shell date +%Y-%m-%dT%H:%M:%SZ) && \

promote_images: qemu
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
	    --push --file $(IMGNAME)/Dockerfile.$${image} . \
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
