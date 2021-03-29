from sqlite3 import Error
import sqlite3
import praw
import configparser
import argparse


config = configparser.ConfigParser()
config.read('conf.ini')
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
reddit_client_id = config['REDDIT']['reddit_client_id']
reddit_client_secret = config['REDDIT']['reddit_client_secret']
reddit_target_subreddit = config['REDDIT']['reddit_target_subreddit']
reddit_target_flair_text = config['REDDIT']['reddit_target_flair_text']
reddit_target_wiki_page = config['REDDIT']['reddit_target_wiki_page']

parser = argparse.ArgumentParser(
    description='Buckethead Recommendations Collector (by u/impshum)')
parser.add_argument(
    '-c', '--collect', type=int, help='collect and update wiki (-c 2000)')
parser.add_argument(
    '-w', '--wiki', help='update wiki only', action='store_true')
parser.add_argument(
    '-r', '--read', help='read all from database', action='store_true')
parser.add_argument(
    '-d', '--drop', help='drop all from database', action='store_true')
args = parser.parse_args()


def db_connect():
    try:
        conn = sqlite3.connect('data.db')
        create_table = """CREATE TABLE IF NOT EXISTS posts (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        post_id TEXT NOT NULL,
                                        title TEXT NOT NULL,
                                        url TEXT NOT NULL,
                                        author TEXT NOT NULL
                                        );"""
        conn.execute(create_table)
        return conn
    except Error as e:
        print(e)
    return None


def reddit_connect():
    return praw.Reddit(
        username=reddit_user,
        password=reddit_pass,
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent='Buckethead Recommendations Collector (by u/impshum)'
    )


def insert_row(conn, post_id, title, url, author):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM posts WHERE post_id = ?", (post_id,))
    if not cur.fetchone():
        conn.execute('INSERT INTO posts (post_id, title, url, author) VALUES (?, ?, ?, ?);',
                     (post_id, title, url, author))
        return True


def read_db(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts;")
    rows = cur.fetchall()
    for row in rows:
        print(row)


def drop_db(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE posts;")
    print('Dropped database')


def get_stats(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT author, count(author) FROM posts GROUP by author ORDER BY count(author) DESC")
    rows = cur.fetchall()

    stats = f'\n\n### Buckethead Recommenders\n\n'
    for row in rows:
        stats += f'u/{row[0]} ({row[1]}) | '

    return stats[:len(stats) - 3]


def write_to_wiki(conn, reddit):
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts")
    rows = cur.fetchall()

    new_wiki = f'### Buckethead Recommendations\n\n'
    for row in rows:
        new_wiki += f'* {row[2]} | [Link]({row[3]})\n'

    new_wiki += get_stats(conn)

    reddit.subreddit(reddit_target_subreddit).wiki[reddit_target_wiki_page].edit(
        content=new_wiki)
    print('Updated wiki')


def main():
    conn = db_connect()

    if args.read:
        read_db(conn)
    elif args.drop:
        drop_db(conn)
    elif args.wiki:
        reddit = reddit_connect()
        write_to_wiki(conn, reddit)
    elif args.collect:
        print(f'Collecting')
        reddit = reddit_connect()
        new = 0

        for submission in reddit.subreddit(reddit_target_subreddit).new(limit=args.collect):
            # print(vars(submission))
            if submission.link_flair_text == reddit_target_flair_text:
                post_id = submission.id
                title = submission.title
                url = submission.url
                author = submission.author.name

                if insert_row(conn, post_id, title, url, author):
                    new += 1

        print(f'Collected {new}')

        if new:
            conn.commit()
            write_to_wiki(conn, reddit)


if __name__ == '__main__':
    main()
