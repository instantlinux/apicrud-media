# Getting Started

### Usage

Photo and video resource storage requires an AWS S3 bucket or compatible service. Obtain an API key from your provider first, and set up an empty S3 bucket.

Clone this repo to your local environment. To start the example application in a shell session (on a Linux or Mac laptop), first follow the usage instructions in [APIcrud Getting Started](https://apicrud.readthedocs.io/en/latest/gettingstarted.html) and then:

* Optional: set environment variables (as defined below) if you wish to override default values
* Invoke `make run_media` to bring up the media API
* Invoke `make media_worker` to bring up the media-worker back-end
* Login as `admin` to the example demo UI (usage instructions in apicrud README)
* At upper right, go into Settings and choose Credentials tab
* Add a new entry: `key` is your AWS API key, `secret` is the API secret
* Choose Storage tab, add a new volume: `name` is anything you want, `bucket` is the bucket name you've set up, `credentials` is item from previous step; `CDN service URL` can be filled in from Cloudfront if you've configured it in AWS console
* Confirm that the Settings tab shows the new default storage volume, which will be available upon next login (logout now)
* From the AWS S3 console, select the `Bucket Policy` tab for your volume and copy/paste the [aws-s3-policy.json](aws-s3-policy.json) file from this github repo into the policy editor. Adjust the bucket name and account number to match yours.
* In the `CORS configuration` tab in the same S3 screen, copy/paste the [aws-cors.xml](aws-cors.xml) file into the configuration editor. Adjust the AllowedOrigin URL to match the hostname/port you're using for testing. Add additional CORSRule stanzas if you serve the page from more than one top-level URL.

### Environment variables

Variable | Default | Description
-------- | ------- | -----------
AMQ_HOST | `example-rmq` | IP address or hostname of rabbitMQ
DB_HOST | `10.101.2.30` | IP address or hostname of MySQL-compatible database
DB_NAME | `example_local` | Name of the database
DOMAIN | | Domain for service URLs
KUBECONFIG | | Config credentials filename for k8s
MEDIA_API_PORT | `8085` | TCP port for media API service
RABBITMQ_IP | `10.101.2.20` | IP address to use for rabbitMQ under k8s
REDIS_IP | `10.101.2.10` | IP address for redis under k8s
