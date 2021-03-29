## Buckethead Recommendations Collector

Grabs all the recommendations from r/buckethead and dumps them all in the wiki.

### Instructions

-   Install requirements `pip install -r requirements.txt`
-   Create Reddit (script) app at <https://www.reddit.com/prefs/apps/> and get keys
-   Edit conf.ini with your details
-   Run it `python run.py -c 2000`

### Help

    usage: run.py [-h] [-w] [-r] [-d]

    optional arguments:
    -h, --help            show this help message and exit
    -c, --collect         collect and update wiki (-c 2000)
    -w, --wiki            update wiki only
    -r, --read            read all from database
    -d, --drop            drop all from database

Run it without any arguments ro run the collector.

### Info

* Max collect is 2000 posts.
* Database file will be created at ```/data.db```.
* Uses SQLite as the database (Use this to browse/edit it https://sqlitebrowser.org/).


### Tip

BTC - 1AYSiE7mhR9XshtS4mU2rRoAGxN8wSo4tK
