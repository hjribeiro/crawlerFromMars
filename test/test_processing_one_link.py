import crawlerFromMars
import aiohttp

# due to time limit I'm using wiremock setting up a local server on localhost:8080 to test


async def test_crawling_stubs_sucessfully():

    # requires wiremock container running omn port 8080
    url = "http://localhost:8080"

    crawlerFromMars.BASE_URL = "http://localhost:8080"
    local_urls = set()
    new_urls = {url}
    external_urls = set()
    broken_urls = set()
    processed_urls = set()

    async with aiohttp.ClientSession() as session:

        await crawlerFromMars.crawl_url(
            broken_urls=broken_urls,
            external_urls=external_urls,
            new_urls=new_urls,
            url=url,
            local_urls=local_urls,
            processed_urls=processed_urls,
            session=session,
        )

    expected_new_urls = {
        "http://localhost:8080/faq",
        "http://localhost:8080/lessons",
        "http://localhost:8080/login",
        "http://localhost:8080/pages",
        "http://localhost:8080/remote",
        "http://localhost:8080/table?row=1",
    }

    expected_processed_urls = {"http://localhost:8080"}
    expected_external_urls = {
        "http://facebook.com/login",
        "http://community.localhost:8080/forum",
    }
    expected_broken_urls = set()

    assert expected_new_urls == new_urls
    assert expected_broken_urls == broken_urls
    assert expected_processed_urls == processed_urls
    assert expected_external_urls == external_urls
