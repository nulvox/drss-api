# drss-api
RSS feed consumer that leverages the WebUI API (rather than a deluge plugin)

# Why?
There are several noteworthy competitors which work very well in most contexts, most notably [YaRSS2](https://deluge-torrent.org/plugins/yarss2/), but I have found that these competitors almost universally act as plugins which may not always be a desireable architecture for your RSS consumer. 

Example scenarios for this tool:
  * the [LSIO deluge container]() is challenging to install the plugin to (or any plugins really)
  * the RSS feeds are inaccessible to your client
  * you just don't like plugins? :shrug:

# What?
This tool consumes a list of rss feeds (`feeds.txt`) and your webUI credentials (`$DUN`, `$DPW`, and `$DURL`) then adds torrents with the configured auto-remove rules (in deluge auto-managed rules) via the webui API. That simple.

# How?

## Deps
This tool's execution environment needs:
  - your creds defined in the env vars (or at the cli)
  - python3 available in $PATH
  - the python packages venv and pip installed
  - valid feeds.txt file
  - a working deluge webui available on the network
  - this repo cloned

## Setup
```
cd drss-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running
```
./drss.py -F feeds.txt  
```

## Setting up a service
this is system-dependent, but you will need to ensure the requirements are available to the system python installation and a way to catch the stdout is handled.
