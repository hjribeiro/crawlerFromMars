import crawlerFromMars
from click.testing import CliRunner
import time


def test_with_successes_and_broken_links_and_timeouts_and_server_disc(caplog):

    expected_external = {
        "http://community.localhost:8080/forum",
        "http://facebook.com/login",
        "http://meetsinglesinuyourarea.com",
        "mailto:complaint@sapo.pt/",
    }
    expected_sitemap = {
        "http://localhost:8080/pages",
        "http://localhost:8080/login",
        "http://localhost:8080/table?row=1",
        "http://localhost:8080/faq",
        "http://localhost:8080/end",
        "http://localhost:8080",
        "http://localhost:8080/remote",
        "http://localhost:8080/lessons",
    }
    expected_broken = {
        "http://localhost:8080/faq",
        "http://localhost:8080/login",
        "http://localhost:8080/lessons",
    }

    start = time.time()
    runner = CliRunner()
    result = runner.invoke(crawlerFromMars.cli, ["http://localhost:8080"])
    end = time.time()
    assert result.exit_code == 0

    # sum of all delays is bigger than 12 seconds - total execution should be less as urls are hit in parallel
    assert end - start < 12

    broken = set()
    with open("output/broken.txt") as broken_txt:
        for line in broken_txt:
            broken.add(line.replace("\n", ""))

    sitemap = set()
    with open("output/sitemap.txt") as sitemap_txt:
        for line in sitemap_txt:
            sitemap.add(line.replace("\n", ""))

    external = set()
    with open("output/external.txt") as external_txt:
        for line in external_txt:
            external.add(line.replace("\n", ""))

    assert expected_sitemap == sitemap
    assert expected_broken == broken
    assert expected_external == external

    # assert all broken urls were properly logged:
    # 3 broken urls, unknown exception print 2 lines - url and exception
    logs = caplog.messages

    assert len(logs) == 4

    assert "got a non 2XX response from: http://localhost:8080/login" in logs
    assert "failed to process url: http://localhost:8080/faq" in logs
    assert "Error: ServerDisconnectedError" in logs
    assert (
        "time out when attempted to process url: http://localhost:8080/lessons" in logs
    )
