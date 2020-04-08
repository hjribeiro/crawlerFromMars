"""crawlerFromMars (cfm) a webcrawler

cfm will crawl over one domain (example.org) and recursively build a
sitemap.txt file with all the links

This script requires pip to install a list of requirements:
just run 'pip install -r requirements.txt'


"""

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urljoin, urldefrag
import asyncio
import aiohttp
import logging
import time
import itertools
import click


logger = logging.getLogger("CFM")

# not sure about ignoring just based on extensions, but seems counterproductive to get a 100MB pdf for example
IGNORE_EXTENSIONS = [
    "zip",
    "pdf",
    "img",
    "doc",
    "txt",
    "jpeg",
    "jpg",
]

# variables are overwritten by 'click'
DEFAULT_MAX_REQUESTS = 20
BASE_URL = "http://example.org"


async def crawl_url(
    url, new_urls, processed_urls, local_urls, external_urls, broken_urls, session
):
    """hits one url and updates the list of new urls to process and processed

        Parameters
        ----------
        url : str
            the url to hit
        new_urls : set
            the list containing all new urls to be hit. It's updated on execution.
        processed_urls: set
            set containing the urls processed so far. updated with 'url' on execution
        local_urls: set
            set containing the local_urls. updated during execution.
        external_urls: set
            same as 'local_urls' except it contains foreign links (different base url). Updated.
        broken_urls: set
            set with urls that did nto work.
        session:
            aiohttp session to be shared with requests. Simpler ro share one session,
            however there could have been performance gain on having one session per request.

        Returns
        -------
        None
    """

    try:
        logging.debug("Processing %s" % url)
        new_urls.remove(url)
        processed_urls.add(url)

        try:
            resp, response = await get_url(session, url)
        except UnicodeDecodeError:
            broken_urls.add(url)
            return

        if resp.status > 299 or resp.status < 200:
            logger.warning(f"got a non 2XX response from: {url}")
            logger.debug(f"still trying to parse contents from url")
            broken_urls.add(url)

        parse_links(url, response, local_urls, external_urls)
        find_new_links_to_crawl(local_urls, processed_urls, new_urls)

        processed_urls.add(url)
    # exception catching is too broad, should have a retry_urls_set
    #  to use to retry on 5XX erros and timeouts
    except asyncio.TimeoutError as to:
        logger.error(f"time out when attempted to process url: {url}")
        broken_urls.add(url)
        return
    except Exception as e:
        logger.error(f"failed to process url: {url}")
        exc_type = str(type(e))
        exc_type = exc_type[exc_type.rfind(".") + 1 : -2]
        logger.error(f"Error: {exc_type}")
        broken_urls.add(url)
        return


async def get_url(session, url):
    async with session.get(url, timeout=10) as resp:
        response = await resp.text()
    return resp, response


def parse_links(url, http_response, local_urls, external_urls):
    """build the sets of local and foreign urls to crawl, based on a
        http response as text

        Parameters
        ----------
        url: str
            the url that generated the http response
        http_response: text
            text response from hitting 'http://{base_url}/{path}'
        local_urls: set
            set containing the local_urls. updated during execution with links found on http_response
        external_urls: set
            same as 'local_urls' except it contains foreign links (different base url). Updated.


        Returns
        -------
        None
    """

    parsed_html = BeautifulSoup(http_response, "lxml")
    for link in parsed_html.find_all("a"):
        anchor = link.attrs.get("href", "")
        process_anchor(anchor, external_urls, local_urls, url)


def process_anchor(anchor, external_urls, local_urls, url):
    split_anchor = urlsplit(anchor)

    # 3 scenarios:
    # local relative path (mind the ../)
    # local absolute path
    # http: url (could still point at same domain)

    # exclude non http(s) (ie mailto: ):
    if split_anchor.scheme and not split_anchor.scheme.startswith("http"):
        external_urls.add(anchor)
    # http(s) can be external or not
    elif split_anchor.scheme:
        domain = split_anchor.netloc.replace("wwww.", "")
        if domain == urlsplit(BASE_URL).netloc:
            anchor = anchor.replace("https:", "http:")
            if anchor.endswith("/"):
                anchor = anchor[:-1]
            anchor = urldefrag(anchor).url
            local_urls.add(anchor)
        else:
            external_urls.add(anchor)
    # absolute and relative paths paths
    else:
        new_url = urljoin(url, anchor)
        if new_url.endswith("/"):
            new_url = new_url[:-1]
        new_url = urldefrag(new_url).url
        local_urls.add(new_url)


def find_new_links_to_crawl(local_urls, processed_urls, new_urls):
    """parses local_urls and updates new_urls
        by default ignores some extensions (my heart's not set on that)

        Parameters
        ----------
        local_urls: set
            set containing local_urls.
        processed_urls: set
            set containing all processed urls so far
        new_urls: set
            Updated with unique new urls from 'local_urls' and not in 'processed_urls'


        Returns
        -------
            None
        """

    for link in local_urls:
        if not link in new_urls and not link in processed_urls:
            if link[link.rfind(".") + 1 :] in IGNORE_EXTENSIONS:
                processed_urls.add(link)
            else:
                new_urls.add(link)


async def main():
    start = time.time()
    url = BASE_URL
    new_urls = set()
    new_urls.add(url)
    processed_urls = set()
    local_urls = set()
    foreign_urls = set()
    broken_urls = set()

    # will run up to a maximum of DEFAULT_MAX_REQUESTS at the same time
    # sharing the same session is easier, to have different session per request it would have to manage tcp layer to
    # a tcp handshake per request
    try:
        async with aiohttp.ClientSession() as session:
            while len(new_urls):
                # get a slice of N
                coroutines = [
                    crawl_url(
                        url,
                        new_urls,
                        processed_urls,
                        local_urls,
                        foreign_urls,
                        broken_urls,
                        session,
                    )
                    for url in itertools.islice(new_urls, DEFAULT_MAX_REQUESTS)
                ]

                # will wait for successful execution of this batch,
                # not true concurrency as if one coroutine finishes quicker still has to wait for all.
                await asyncio.gather(*coroutines)
                logger.info(
                    f"processed {len(coroutines)} urls to a total of {len(processed_urls)}"
                )
                coroutines.clear()
    except Exception as e:
        logger.error(type(e))

    with open("output/sitemap.txt", "w") as f:
        for item in processed_urls:
            f.write("%s\n" % item)

    with open("output/broken.txt", "w") as f:
        for item in broken_urls:
            f.write("%s\n" % item)

    with open("output/external.txt", "w") as f:
        for item in foreign_urls:
            f.write("%s\n" % item)

    now = time.time()
    elapsed = int(now - start)
    logger.info(f"processed {len(processed_urls)} links in {elapsed} sec")
    logger.info("output file: output/sitemap.txt")


# Command line library
@click.command()
@click.option(
    "--maxParallelRequests", default=20, help="number of max parallel requests"
)
@click.option("--debug", is_flag=True, help="debug log flag")
@click.argument("url")
def cli(maxparallelrequests, url, debug):
    # default max of 20 requests at the same time.
    # tested with a few values, this seemed to work relatively fast and not cause disconnection from site
    global DEFAULT_MAX_REQUESTS, BASE_URL
    DEFAULT_MAX_REQUESTS = maxparallelrequests

    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(message)s", level=log_level,
    )

    parsed = urlsplit(url)
    domain = parsed.netloc
    domain = domain.replace("www.", "")
    scheme = parsed.scheme
    scheme = scheme.replace("https:", "http:")
    if not domain:
        logger.error("invalid url: ", url)
    BASE_URL = f"{scheme}://{parsed.netloc}"

    asyncio.run(main())


if __name__ == "__main__":
    cli()
