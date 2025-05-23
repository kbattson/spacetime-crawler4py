import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
import pagedata
import sqlite3


#TODO
'''
- implement politeness delays, might be included in base crawler not sure
- detect and avoid infinite traps
    - calendars
- avoid URLS with 200 status but no data (blacklist maybe? not sure)
- avoid crawling very large files
- exact/near exact page similariy detection

- write program to tokenize and extract metrics from crawler_data.db
'''

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def normalize_url(url):
    url, _ = urldefrag(url)
    url = url.lower()
    if '?' in url:
        url = url[:url.find('?')]
    return url

previous_call_urls = []

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!

    global previous_call_urls

    with sqlite3.connect('crawler_data.db') as conn:

        if resp.status == 200 and resp.raw_response and resp.raw_response.content:
            try:
                pagedata.store_page(conn, normalize_url(resp.url), resp.raw_response.content)
                
                soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
                urls = [normalize_url(urljoin(url, a['href'])) for a in soup.find_all('a', href=True)]
                urls = list(set(urls))

                # trap detection

                # checking for one-off traps
                # generally found in chained calls of this function so we store the last call
                # does there exist a url in the previous call that is +1 length and otherwise the same?
                filtered_urls = []
                for curr_url in urls:
                    is_trap = False
                    for prev_url in previous_call_urls:
                        if len(prev_url) - 1 == len(curr_url) and curr_url in prev_url:
                            is_trap = True
                            break

                    if not is_trap:
                        filtered_urls.append(curr_url)

                previous_call_urls = filtered_urls.copy()
                urls = filtered_urls

                return [url for url in urls if 
                        not pagedata.is_visited(conn, url) 
                        and not pagedata.is_blacklisted(conn, url)]

            except Exception as e:
                print(f"Error during parsing: {e}")
                return []
        else:
            pagedata.blacklist_url(conn, normalize_url(url), resp.error)
            return []

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # netloc is the domain of the parsed url
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        
        if not (netloc.endswith('.ics.uci.edu') or
                netloc.endswith('.cs.uci.edu') or
                netloc.endswith('.informatics.uci.edu') or
                netloc.endswith('.stat.uci.edu') or
                (netloc == 'today.uci.edu' and path.startswith('/department/information_computer_sciences'))):
                return False

        if 'account' in netloc or 'git' in netloc or 'login' in netloc:
            return False

        if netloc.startswith('fano') or netloc.startswith('swiki') or netloc.startswith('helpdesk') or netloc.startswith('grape'):
            return False

        date_pattern = r'/(19|20)\d{2}[-/](0[1-9]|1[0-2])([-/](0[1-9]|[12][0-9]|3[01]))?/'
        if re.search(date_pattern, path):
            return False

        login_signup_pattern = r'/login|signin|signup|register|forgot|reset|change|update|delete|logout'
        if re.search(login_signup_pattern, path):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            # .mpg is video/audio format
            # .lif is collection of images
            # apk is android something something 
            # pd = pure datak
            # jp = jpeg
            # ppsx is mc powerpoint
            # bam is Binary Alignment Map
            + r"|mpg|lif|apk|pd|jp|img|ppsx|ipynb|bib|bam)$"
            , parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise















