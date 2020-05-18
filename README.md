## apicrud-media
[![](https://images.microbadger.com/badges/image/instantlinux/apicrud-media.svg)](https://microbadger.com/images/instantlinux/apicrud-media "Image badge") [![](https://gitlab.com/instantlinux/apicrud-media/badges/master/pipeline.svg)](https://gitlab.com/instantlinux/apicrud-media/pipelines "pipelines") [![](https://gitlab.com/instantlinux/apicrud-media/badges/master/coverage.svg)](https://gitlab.com/instantlinux/apicrud-media/-/jobs/artifacts/master/file/apicrud-media/htmlcov/index.html?job=analysis "coverage")

### What is this

Skip the kubernetes / python / React.js learning curve and put your ideas in production!

The _apicrud_ framework makes it far easier to get started on full-stack development of REST-based services, ranging from a simple CLI wrapper for queries of local APIs to full web-scale consumer-facing applications running on kubernetes.

The essential components of a modern full-stack application include a back-end API server, a front-end UI server, a database, a memory-cache and a background worker for performing actions such as emailing, photo uploading or report generation. The challenge of setting up CI testing and microservice deployment is usually daunting; this repo addresses all of those issues by providing a fully-working example you can set up and start modifying in minutes. No prior experience is required.

This is the media-service API back-end and worker, for the _example_ application.

### Usage

Photo and video resource storage requires an AWS S3 bucket or compatible service. Obtain an API key from your provider first, and set up an empty S3 bucket.

Clone this repo to your local environment. To start the example application in a shell session (on a Linux or Mac laptop), first follow the usage instructions in [apicrud README](https://github.com/instantlinux/apicrud/blob/master/README.md) and then:

* Optional: set environment variables (as defined below) if you wish to override default values
* Invoke `make run_media` to bring up the media API
* Invoke `make media_worker` to bring up the media-worker back-end
* Login as `admin` to the example demo UI (usage instructions in apicrud README)
* At upper right, go into Settings and choose Credentials tab
* Add a new entry: `key` is your AWS API key, `secret` is the API secret
* Choose Storage tab, add a new volume: `name` is anything you want, `bucket` is the bucket name you've set up, `credentials` is item from previous step; `CDN service URL` can be filled in from Cloudfront if you've configured it in AWS console
* Confirm that the Settings tab shows the new default storage volume
* From the AWS S3 console, select the `Bucket Policy` tab for your volume and copy/paste the [aws-s3-policy.json](aws-s3-policy.json) file from this github repo into the policy editor. Adjust the bucket name and account number to match yours.
* In the `CORS configuration` tab in the same S3 screen, copy/paste the [aws-cors.xml](aws-cors.xml) file into the configuration editor. Adjust the AllowedOrigin URL to match the hostname/port you're using for testing. Add additional CORSRule stanzas if you serve the page from more than one top-level URL.

### Environment variables

Variable | Default | Description
-------- | ------- | -----------
AMQ_HOST | `example-rmq` | IP address or hostname of rabbitMQ
API_DEV_PORT | `32080` | TCP port for API service (local dev k8s)
DB_HOST | `10.101.2.30` | IP address or hostname of MySQL-compatible database
DB_NAME | `example_local` | Name of the database
DOMAIN | | Domain for service URLs
EXAMPLE_API_PORT | `8080` | TCP port for API service
KUBECONFIG | | Config credentials filename for k8s
RABBITMQ_IP | `10.101.2.20` | IP address to use for rabbitMQ under k8s
REDIS_IP | `10.101.2.10` | IP address for redis under k8s

### Secrets

Kubernetes needs secrets defined. Default values for these are under example/secrets/. See the [example/Makefile.sops](https://github.com/instantlinux/apicrud/blob/master/example/Makefile.sops) (and the lengthy [kubernetes secrets doc](https://kubernetes.io/docs/concepts/configuration/secret/) for instructions on modifying them or adding new secrets for multiple namespace environments.

Secret | Description
------ | -----------
example-db-aes-secret | Encryption passphrase for secured DB columns (~16 bytes)
example-db-password | Database password
example-flask-secret | Session passphrase (32 hex digits)
example-redis-secret | Encryption passphrase for redis values (~16 bytes)
mariadb-root-password | Root password for MariaDB

### Contributions

Your pull-requests and bug-reports are welcome here. See [CONTRIBUTING.md](CONTRIBUTING.md).

### License

Software copyright &copy; 2020 by Richard Braun &bull; <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a> license <p />
