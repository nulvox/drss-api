#!/usr/bin/env python3
import argparse, feedparser, json, requests, urllib
from deluge_web_client import DelugeWebClient
from os import environ,path

parser = argparse.ArgumentParser()
parser.add_argument(
    "-F",
    "--feedsfile",
    help="Path to a file containing a list of RSS feed URLs 1 URL per line",
    required=True,
)
# parser.add_argument("-R", "--rules-file", help="Path to a file with the rss content filter rules... tbd")
parser.add_argument(
    "-p",
    "--password",
    help="Deluge webui password, defaults to env $DPW and will not proceed without a value supplied.",
    default=environ.get("DPW", default=""),
)
parser.add_argument(
    "-d",
    "--delugeurl",
    help="URL to the deluge instance, defaults to env $DURL and falls back to '127.0.0.1:8112'",
    default=environ.get("DURL", default="http://127.0.0.1:8112"),
)
parser.add_argument(
    "-D",
    "--dryrun",
    action="store_true",
    help="Don't add torrents, just do a dry run",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Make more output",
)
args = parser.parse_args()

# ensure creds were supplied to do the work
if args.password is None:
    raise ValueError("$DPW and -p are not defined with a valid deluge Webui password")


# set up a file size string interpreter
class fsi:
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    @classmethod
    def interpret(cls, size_str):
        size_str = size_str.strip().upper()
        for unit in cls.units:
            if size_str.endswith(unit):
                number = float(size_str[: -len(unit)].strip())
                return int(number * cls.units[unit])
        raise ValueError("Invalid file size string")


# supply the existing deluge context and a given torrentspec
# return a bool for if it is already active
def already_active(torrent, context):
    target_name = torrent["title"]
    for tid, info in context:
        if info["name"] == target_name:
            return True
    return False


# Check how much the disk quota will overflow if we add the torrent
def check_limit(delta, dc):
    free_space_resp = dc.get_free_space(path="rss")
    free_space = free_space_resp.result
    return float(delta) - float(free_space)


# open the feed list file and generate the list object
def get_feed_list(feed_file):
    with open(feed_file, "r") as feeds:
        return feeds.readlines()

# download the torrent file from the feed
#  return a string with the path to the file
def download_torrentfile(torrent):
    
    pass

def main():
    # ensure the deluge service is running and likes your creds
    dc = DelugeWebClient(url=args.delugeurl, password=args.password)
    dc.login()
    context = dc.get_torrents_status(keys=["name"])
    feedlist = get_feed_list(args.feedsfile)
    if not feedlist:
        raise ValueError("No feed list supplied.")
    # loop over RSS feeds to work our magic
    for feed in feedlist:
        # runs check_limit on self
        if not check_limit(0, dc):
            # breaks the loop if the limit is already met or exceeded
            print(
                "Deluge Server limits already met or exceeded, ending feed processing."
            )
            break
        # build the feed parser
        candidate_url = True
        try:
            urllib.parse.urlparse(feed)
        except:
            print(f"Invalid url {feed} in list, assuming local file...")
            candidate_url = False
            if not (candidate_url and path.exists(feed) and path.isfile(feed)):
                print(f"Not a valid url or filepath... continuring loop...")
                continue
        try:
            content = feedparser.parse(feed)
        except Exception as e:
            print(e)
            print(f"Cloud not fetch rss feed {feed}, continuing loop..")
            continue
        print("setting feed...")
        content = feedparser.parse(feed)
        print(f"using this content:\n{content}")
        for torrent in content["entries"]:
            if args.verbose:
                print(f"checking torrent {torrent}")
            if check_limit(0, dc) > 0:
                print(
                    "Deluge server limits already met or exceeded, ending feed processing for {feed}."
                )
                break
            if already_active(torrent, context):
                print(f"Torrent {torrent} is already active, continuing loop...")
                continue
            sizeh = torrent["summary_detail"]["value"].split(";")[0]
            size = fsi.interpret(sizeh)
            if check_limit(size, dc) > 0:
                print(
                    f"Torrent {torrent} with size {sizeh} exceeds the remaining limits, continuing loop..."
                )
                continue
            # add secondary filters here (ie, stop hosting TSwizzle)
            if args.dryrun:
                print(f"Pretending to add torrent {torrent}")
                continue
            torrent_file = download_torrentfile(torrent)
            upload = dc.upload_torrent(
                torrent_path=torrent_file,
                add_paused=False,
                label="drss-managed",
                seed_mode=False,
                auto_managed=True,
            )
            if not upload["error"]:
                print(f"adding torrent {torrent} with hash {upload['result']}")
                context = dc.get_torrents_status(keys=["name"])


if __name__ == "__main__":
    main()
