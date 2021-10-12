## apicrud-media
[![](https://img.shields.io/docker/v/instantlinux/apicrud-media?sort=date)](https://microbadger.com/images/instantlinux/apicrud-media "Image badge") [![](https://gitlab.com/instantlinux/apicrud-media/badges/main/pipeline.svg)](https://gitlab.com/instantlinux/apicrud-media/pipelines "pipelines") [![](https://gitlab.com/instantlinux/apicrud-media/badges/main/coverage.svg)](https://gitlab.com/instantlinux/apicrud-media/-/jobs/artifacts/main/file/apicrud-media/htmlcov/index.html?job=analysis "coverage") ![](https://img.shields.io/badge/platform-amd64%20arm64%20arm%2Fv6%20arm%2Fv7-blue "Platform badge") [![](https://img.shields.io/badge/dockerfile-latest-blue)](https://gitlab.com/instantlinux/apicrud-media/-/blob/main/Dockerfile.media "dockerfile")

### What is this

Skip the kubernetes / python / React.js learning curve and put your ideas in production!

The _apicrud_ framework makes it easier to get started on full-stack development of REST-based services, ranging from a simple CLI wrapper for queries of local APIs to full web-scale consumer-facing applications running on kubernetes.

The essential components of a modern full-stack application include a back-end API server, a front-end UI server, a database, a memory-cache and a background worker for performing actions such as emailing, photo uploading or report generation. The challenge of setting up CI testing and microservice deployment is usually daunting; this repo addresses all of those issues by providing a fully-working example you can set up and start modifying in minutes. No prior experience is required.

This is the media-service API back-end and worker, for the _example_ application.

### Usage

See the [getting started](docs/content/gettingstarted.md) page, or navigate to [Read the Docs](https://apicrud-media.readthedocs.io/).

### Contributions

Your pull-requests and bug-reports are welcome here. See [CONTRIBUTING.md](CONTRIBUTING.md).

### License

Software copyright &copy; 2021 by Richard Braun &bull; <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a> license <p />
