import re
import csv
import urllib.request
from bs4 import BeautifulSoup

# This file takes a csv of the top sites and checks for how many of them use DNS Prefetching
# Written for python3
# https://dev.chromium.org/developers/design-documents/dns-prefetching
def main():
        # total websites reviewed
        totalsites = 0
        # websites with rel="dns-prefetch
        linkrel = 0
        # websites with meta http-equiv="x-dns-prefetch-control"
        metadns = 0

        # compile regex
        #linkrelreg = re.compile(r"link\W+href=\"[a-zA-Z0-9\/\.]+\"\W+rel=\"dns-prefetch\"", re.IGNORECASE)

        with open("top-1m.csv", "r") as webcsv:
                rdr = csv.reader(webcsv, delimiter=',')
                for rank, sitename in rdr:
                        # I don't want to visit .ru sites on my network
                        if (".ru" not in sitename):
                                print(sitename)
                                try: 
                                        # HTTPS?
                                        contents = urllib.request.urlopen("http://" + sitename, timeout=10).read()
                                        soup = BeautifulSoup(contents, 'html.parser')
                                        if (soup.find_all(rel="dns-prefetch") != []):
                                                linkrel += 1
                                        for meta in soup.find_all("meta"):
                                                # need to fix case insensitive
                                                metahttp = meta.get('http-equiv', '').lower()
                                                # need to get content on/off?
                                                # metacontent = meta.get('content', '').lower()
                                                if (metahttp == "x-dns-prefetch-control"):
                                                        metadns += 1
                                        totalsites += 1
                                except KeyboardInterrupt:
                                        break
                                except Exception as e:
                                        print("{}: unable to load {}".format(e, sitename))
                                        continue
                                #except urllib.error.URLError:
                                #        print("URLError: unable to load " + sitename)
                                #        continue
                                #except TimeoutError:
                                #        print("TimeoutError: unable to load " + sitename)
                                #        continue
        print("Sites reviewed: {}".format(totalsites))
        print("Sites with rel=\"dns-prefetch\": {}".format(linkrel))
        print("% with rel=\"dns-prefetch\": {}".format(float(linkrel)/totalsites))
        print("Sites specifying some sort of x-dns-prefetch-control: {}".format(metadns))
        print("% with x-dns-prefetch control: {}".format(float(metadns)/totalsites))

if __name__ == "__main__":
        main()
