import crawlerFromMars


def test_finding_new_links():
    local_urls = {
        # link1 is already on new_urls
        "http://local/path1",
        # link 2 is on processed - not added
        "http://local/path2",
        "http://local/path3",
        "http://local/path4",
        "http://local/path5",
        # pdf and jpg not added
        "http://local/pdf.pdf",
        "http://local/image.jpg",
    }

    new_urls = {
        "http://local/path1",
        "http://local/path6",
    }

    processed_urls = {
        "http://local/path2",
        "http://local/path7",
    }

    crawlerFromMars.find_new_links_to_crawl(local_urls, processed_urls, new_urls)

    new_expectd = {
        "http://local/path1",
        "http://local/path6",
        "http://local/path3",
        "http://local/path4",
        "http://local/path5",
    }

    assert new_expectd == new_urls


def test_processing_relative_local_anchors():
    local_urls = set()
    external_urls = set()
    url = "http://domain1.org"
    anchor = "page1"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain1.org/page1"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals

    local_urls.clear()
    external_urls.clear()
    url = "http://domain2.org/something"
    anchor = "../page2"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain2.org/page2"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals


def test_processing_absolute_anchors():
    local_urls = set()
    external_urls = set()
    url = "http://domain1.org/dead-end"
    anchor = "/page1"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain1.org/page1"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals

    local_urls.clear()
    external_urls.clear()
    url = "http://domain2.org/dead-end"
    anchor = "/page2/index.html"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain2.org/page2/index.html"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals


def test_processing_local_url_starting_with_http_and_https():
    crawlerFromMars.BASE_URL = "http://domain1.org"
    local_urls = set()
    external_urls = set()
    url = "http://domain1.org/page1"
    anchor = "http://domain1.org/page2"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain1.org/page2"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals

    crawlerFromMars.BASE_URL = "http://domain2.org"
    local_urls.clear()
    external_urls.clear()
    url = "http://domain2.org/dead-end"
    anchor = "https://domain2.org/page2"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_locals = {"http://domain2.org/page2"}
    assert len(external_urls) == 0
    assert local_urls == expected_locals


def test_processing_exernal_url_starting_with_http_and_https():
    crawlerFromMars.BASE_URL = "http://domain1.org"
    local_urls = set()
    external_urls = set()
    url = "http://domain1.org/page1"
    anchor = "http://domain2.org/page2"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_externals = {"http://domain2.org/page2"}
    assert len(local_urls) == 0
    assert external_urls == expected_externals

    crawlerFromMars.BASE_URL = "http://domain2.org"
    local_urls.clear()
    external_urls.clear()
    url = "http://domain2.org/dead-end"
    anchor = "https://domain3.org/page3"
    crawlerFromMars.process_anchor(anchor, external_urls, local_urls, url)
    expected_externals = {"https://domain3.org/page3"}
    assert len(local_urls) == 0
    assert external_urls == expected_externals
