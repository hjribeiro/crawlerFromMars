# crawlerFromMars

crawlerFrom Mars is a web crawler, that will crawl over links in a domain.
The result of the execution is stored on the folder `output/` as three different files:
- sitemap.txt: the list of url,from the same domain, obtained after crawling
- broken.txt: the list of all broken links (timeouts, HTTP errors and other exceptions)
- external.txt: the list of all links pointing to different domains, or non HTTP links

## Dependencies

- python 3.7

- pipenv [(installation)](https://github.com/pypa/pipenv)
- docker: Tests use a docker image of [wiremock](http://wiremock.org/) to serve HTTP and to cause some special HTTP scenarios likes timeouts and other failures

  

## Usage

- Install dependencies with pienv:
`pipenv install`
- run `pipenv run python crawlerFromMars --help` for usage description.
- to run over __**my-domain**__ simply run: `pipenv run python crawlerFromMars http://mydomain`


## Tests

In order to simulate network failures and timeouts, tests use a docker image of _wiremock_.

From the root folder run:

-  `sh scripts/run_tests.sh`

This will setup mocks and execute tests.

