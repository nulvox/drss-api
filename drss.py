#!/usr/bin/env python3
import argparse, feedparser, json, requests, urllib
from os import environ

# 1. set up argparse (and parse input)
#   a list file for feeds
#   b json file for limits
#   c client secrets file (or env vars? :shrug:)
#   d think about filter rules file?
parser = argparse.ArgumentParser()
parser.add_argument("-F", "--feeds-file", help="Path to a file containing a list of RSS feed URLs 1 URL per line", required=True)
parser.add_argument("-L", "--limits-file", help="Path to a json file describing the limits, sane defaults will be selected.", required=False)
#parser.add_argument("-R", "--rules-file", help="Path to a file with the rss content filter rules... tbd")
parser.add_argument("-u", "--username", help="Deluge webui username, deffaults to env $DUN and falls back to 'admin'", default=environ.get('DUN', default='admin'))
parser.add_argument("-p", "--password", help="Deluge webui password, defaults to env $DPW and will not proceed without a value supplied.", default=environ.get('DPW', default=''))
parser.add_argument("-d", "--deluge-url", help="URL to the deluge instance, defaults to env $DURL and falls back to '127.0.0.1:8112'", default=environ.get('DURL', default='http://127.0.0.1:8112'))
args = parser.parser_args()

# ensure creds were supplied to do the work
if args.password is None:
    raise ValueError('$DPW and -p are not defined with a valid deluge Webui password')

# set up a file size string interpreter
class fsi:
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    @classmethod
    def interpret(cls, size_str):
        size_str = size_str.strip().upper()
        for unit in cls.units:
            if size_str.endswith(unit):
                number = float(size_str[:-len(unit)].strip())
                return int(number * cls.units[unit])
        raise ValueError("Invalid file size string")

# confirm the deluge service is running and accepts the supplied creds
def test_deluge_service(un, pw, url):
    pass

# get the current deluge context
def get_deluge_context(un, pw, url):
    pass

# supply the existing deluge context and a given torrentspec
# return a bool for if it is already active
def already_active(torrent, context):
    pass

# 2. set up the Deluge API client
#   2.5 build the API request template dict to set seeding rules
def new_deluge_client():
    pass

# 3. open the feed list file and generate the list object
def get_feed_list(feed_file):
    with open(feed_file, 'r') as feeds:
        return feeds.readlines()

# 4. begin for loop on feed list
# 5. set up the rssfeed parser block with supplied feed arg
# 6. (bonus) add secondary filtering schema?
# 7. evaluate active torrent and disk limits
# 8. call the api to add relevant torrent
# 9. log the event
# 10. close the loop, and exit

def main():
    # ensure the deluge service is running and likes your creds
    test_deluge_service()
    feedlist = get_feed_list(args.feeds-file)
    if not feedlist:
        raise ValueError('No feed list supplied.')
    limitsdict = get_limits_dict(args.limits-file)
    limits_keys = list(limitsdict.keys())
    missing_fileds = []
    for key in limits_req_fields:
        if field not in limits_keys:
            missing_fileds.append(key)
    if missing_fields:
        raise ValueError(f'The following required fields were not defined in the supplied limits file: {missing_fileds}')
    # loop over RSS feeds to work our magic
    for feed in feedlist:
        # runs check_limit on self
        if not check_limit(0):
            # breaks the loop if the limit is already met or exceeded
            print("Deluge Server limits already met or exceeded, ending feed processing.")
            break
        # build the feed parser
        try: 
            urllib.parse.urlparse(feed)
        except:
            print(f"Invalid url {feed} in list, continuing loop...")
            continue
        try:
            content = feedparser.parser(feed)
        except:
            print(f"Cloud not fetch rss feed {feed}, continuing loop..")
        for torrent in content['entries']:
			if check_limit(0) > 0:
				print("Deluge server limits already met or exceeded, ending feed processing for {feed}.")
				break
			if already_active(torrent, context):
                print(f"Torrent {torrent} is already active, continuing loop...")
                continue
            sizeh = torrent['summary_detail']['value'].split(';')[0]
			size = fsi.interpret(sizeh)
			if check_limit(size) > 0:
				print(f"Torrent {torrent} with size {sizeh} exceeds the remaining limits, continuing loop...")
				continue
			# add secondary filters here (ie, stop hosting TSwizzle)
			add_torrent(torrent, args.username, args.password, args.durl)
			print(f"adding torrent {torrent}")

if __name__ == "__main__":
    main()
