#TODO: HTTPS
#TODO: What are dnsprefetch? Counts, print as results
#TODO: Make file for each of top 10000 (static file) with dns-prefech tags if they exists (mark ones without)

import csv
import zipfile
import time
import datetime
import argparse
import urllib.request
from bs4 import BeautifulSoup

# This file takes a csv of the top sites and checks for how many of them use DNS Prefetching
# Written for python3
# https://dev.chromium.org/developers/design-documents/dns-prefetching
def main():
        # Read cmdline arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", help="print website info when requests go through", action="store_true")
        parser.add_argument("-d", "--debug", help="print site exception info", action="store_true")
        parser.add_argument("-t", "--timeout", help="seconds to wait for a site to timeout", default=5, type=int)
        parser.add_argument("-m", "--max", help="max number of websites to successfully scan before exiting", default=10000, type=int)
        args = parser.parse_args()
        maxsites = args.max
        timeout = args.timeout
        # total websites reviewed
        totalsites = 0
        # websites with rel="dns-prefetch
        linkrel = 0
        # websites with meta http-equiv="x-dns-prefetch-control"
        metadns = 0
        #sites that could not load
        failedsites = 0

        # Check for real timeout time and maxsites
        if (timeout < 1 or maxsites < 1):
                print("Need a positive timeout time")
                quit()

        # get cur time for our file creation
        filetime = time.strftime("%m-%d-%y_%H", time.localtime())

        starttime = datetime.datetime.now() 

        # Reading csv
        with open("top-1m.csv", "r") as webcsv:
                rdr = csv.reader(webcsv, delimiter=',')
                for rank, sitename in rdr:
                        # break if we've gone over the specified max number of sites to check
                        if (totalsites >= maxsites):
                                break
                        # Try cause to catch any exceptions HTTP GETting a website may encounter
                        try: 
                                # vars for printing to individual files
                                rels = []
                                metas = []
                                # Do sites that are HTTP only still connect?
                                contents = getHTTP(sitename, timeout)
                                # contents = urllib.request.urlopen(url, timeout=timeout).read()
                                soup = BeautifulSoup(contents, 'html.parser')
                                if (args.verbose):
                                        print(sitename)
                                if (soup.find_all(rel="dns-prefetch") != []):
                                        linkrel += 1
                                for rel in soup.find_all(rel="dns-prefetch"):
                                        rels.append(rel)
                                for meta in soup.find_all("meta"):
                                        # need to fix case insensitive
                                        metahttp = meta.get('http-equiv', '').lower()
                                        # need to get content on/off?
                                        # metacontent = meta.get('content', '').lower()
                                        if (metahttp == "x-dns-prefetch-control"):
                                                metas.append(meta)
                                                metadns += 1
                                # write results to own file, regardless of if the site was able to connect (?)
                                totalsites += 1
                        except KeyboardInterrupt:
                                break
                        except Exception as e:
                                # Site failed, print site and rank anyway with error message
                                rels.append("Connection failure")
                                writesite(rank, sitename, rels, metas)
                                if (args.debug):
                                        print("{}: unable to load {}".format(e, sitename))
                                failedsites += 1
                                continue

        # Create our output file
        # outname = "/home/ubuntu/sdf/dnsstapling/results/prefetch/{}top{}".format(filetime, maxsites)
        outname = "{}top{}".format(filetime, maxsites)
        print(outname)
        outfile = open(outname, "w")

        outfile.write("Parameters: timeout={} maxsites={}\n".format(timeout, maxsites))
        outfile.write("Sites reviewed: {}\n".format(totalsites))
        outfile.write("Sites with rel=\"dns-prefetch\": {}\n".format(linkrel))
        outfile.write("% with rel=\"dns-prefetch\": {}\n".format(float(linkrel)/totalsites))
        outfile.write("Sites specifying some sort of x-dns-prefetch-control: {}\n".format(metadns))
        outfile.write("% with x-dns-prefetch control: {}\n".format(float(metadns)/totalsites))
        outfile.write("Sites that failed to connect for any reason: {}\n".format(failedsites))
        outfile.write("Ran from {} until {}\n".format(starttime, datetime.datetime.now()))

        outfile.close()


# Determine if link can be used as HTTPS
def getHTTP(sitename, timeout):
        contents = urllib.request.urlopen("https://" + sitename, timeout=timeout).read()
        return contents


# Write site results to an individual file
def writesite(rank, sitename, rels, metas):
        sitefile = open("results/dns_top{}".format(rank), "w")
        # sitefile = open("/wherever/results/dns_top{}".format(rank))
        sitefile.write("https://{}\n".format(sitename))
        # write all rel links
        for tag in rels:
                sitefile.write(str(tag) + "\n")
        # write all dns meta specifiers
        for tag in metas:
                sitefile.write(str(tag) + "\n")
        sitefile.close()

# Use to complete webpage processing
# TODO: Incorporate/ Here if need be
def processurl(sitename, soup):
        if (args.verbose):
                print(sitename)
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

if __name__ == "__main__":
        main()
