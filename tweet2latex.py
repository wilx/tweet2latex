#!/usr/bin/env python

"""
Fetch a single tweet as JSON using its id and output LaTeX.
"""
from __future__ import print_function

import os
import re
import regex
import json
import twarc
import argparse
import sys
import html
from enum import Enum
import six.moves.urllib as urllib
from six import u as unicode
from icu import SimpleDateFormat, DateFormat, Locale
tweetDf = SimpleDateFormat("EEE MMM dd hh:mm:ss xx yyyy", Locale.getUS())


try:
    import configparser  # Python 3
except ImportError:
    import ConfigParser as configparser  # Python 2

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

try:
    # Python 2.6-2.7
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser
htmlParser = HTMLParser()


class CaptionPlacement(Enum):
    top = 'top'
    bottom = 'bottom'

    def __str__ (self):
        return self.value


def load_config(filename, profile):
    if not os.path.isfile(filename):
        return None
    config = configparser.ConfigParser()
    config.read(filename)
    data = {}
    for key in ['access_token', 'access_token_secret',
                'consumer_key', 'consumer_secret']:
        try:
            data[key] = config.get(profile, key)
        except configparser.NoSectionError:
            sys.exit("no such profile %s in %s" % (profile, filename))
        except configparser.NoOptionError:
            sys.exit("missing %s from profile %s in %s" % (
                     key, profile, filename))
    return data

def default_config_filename():
    """
    Return the default filename for storing Twitter keys.
    """
    home = os.path.expanduser("~")
    return os.path.join(home, ".twarc")

def escape_latex_basic(str):
    tmp = u''
    for ch in str:
        if ch == '\\':
            tmp += '\\textbackslash '
        elif (ch == '_' or ch == '#' or ch == '%' or ch == '^'
                or ch == '{' or ch == '}' or ch == '&'):
            tmp += '\\'
            tmp += ch
        else:
            tmp += ch
    return tmp

def tweak_filename(str):
    return str.replace('_', '-')

def check_file_viable(filename):
    return os.path.isfile(filename) and os.path.getsize(filename) > 0


e = os.environ.get
parser = argparse.ArgumentParser("tweet.py")

parser.add_argument('tweet_id', action="store", help="Tweet ID")
parser.add_argument("--consumer_key", action="store",
                    default=e('CONSUMER_KEY'),
                    help="Twitter API consumer key")
parser.add_argument("--consumer_secret", action="store",
                    default=e('CONSUMER_SECRET'),
                    help="Twitter API consumer secret")
parser.add_argument("--access_token", action="store",
                    default=e('ACCESS_TOKEN'),
                    help="Twitter API access key")
parser.add_argument("--access_token_secret", action="store",
                    default=e('ACCESS_TOKEN_SECRET'),
                    help="Twitter API access token secret")
parser.add_argument('-c', '--config',
                    default=default_config_filename(),
                    help="Config file containing Twitter keys and secrets")
parser.add_argument('-p', '--profile', default='main',
                    help="Name of a profile in your configuration file")
parser.add_argument("--pdflatex", action="store_true",
                    default=False, required=False,
                    help="Produce PDFLaTeX compatible output.")
parser.add_argument("--caption", action="store_true",
                    default=False, required=False,
                    help="Add caption to generated LaTeX.")
parser.add_argument("--caption-placement", action="store",
                    type=CaptionPlacement, choices=list(CaptionPlacement),
                    default='top', required=False,
                    help="Caption placement. (default: top)")
parser.add_argument("--keep-spaces", action="store_true",
                    default=False, required=False,
                    help="Try to keep extra space characters.")


args = parser.parse_args()

consumer_key = args.consumer_key or os.environ.get('CONSUMER_KEY')
consumer_secret = args.consumer_secret or os.environ.get('CONSUMER_SECRET')
access_token = args.access_token or os.environ.get('ACCESS_TOKEN')
access_token_secret = args.access_token_secret or os.environ.get('ACCESS_TOKEN_SECRET')
use_pdflatex = args.pdflatex
caption = args.caption
caption_placement = args.caption_placement
keep_spaces = args.keep_spaces

if not (consumer_key and consumer_secret and
        access_token and access_token_secret):
    credentials = load_config(args.config, args.profile)
    if credentials:
        consumer_key = credentials['consumer_key']
        consumer_secret = credentials['consumer_secret']
        access_token = credentials['access_token']
        access_token_secret = credentials['access_token_secret']
    else:
        sys.exit("Please supply Twitter authentication credentials.")

tweetJsonFile = '%s.json' % args.tweet_id
tj = None
if check_file_viable(tweetJsonFile):
    with open(tweetJsonFile, 'r') as infile:
        tj = json.load(infile)
else:
    tw = twarc.Twarc(consumer_key, consumer_secret, access_token, access_token_secret, tweet_mode='extended')
    tweet = tw.get('https://api.twitter.com/1.1/statuses/show/%s.json' % args.tweet_id,
                   params={'tweet_mode':'extended'}, allow_404=True)
    tj = tweet.json()
    with open(tweetJsonFile, 'w') as outfile:
        json.dump(tj, outfile, indent=2, sort_keys=True)

decorationsStart = dict()
decorationsEnds = dict()

# Find all hashtags and enter them into entities table.

entitiesDict = tj.get('entities', None)
if entitiesDict is not None:
    # Hashtags
    for hashtagRec in entitiesDict.get('hashtags', list()):
        start = hashtagRec['indices'][0]
        end = hashtagRec['indices'][1]
        assert start not in decorationsStart
        decorationsStart[start] = ('\\tweetHashtag{'
                                       + hashtagRec['text']
                                       + '}{')
        assert end not in decorationsEnds
        decorationsEnds[end] = '}'
    # User mentions
    for userMentionRec in entitiesDict.get('user_mentions', list()):
        start = userMentionRec['indices'][0]
        end = userMentionRec['indices'][1]
        assert start not in decorationsStart
        decorationsStart[start] = '\\tweetUserMention{' + userMentionRec['id_str'] + '}{'
        assert end not in decorationsEnds
        decorationsEnds[end] = '}'
    # URLs
    for urlRec in entitiesDict.get('urls', list()):
        start = urlRec['indices'][0]
        end = urlRec['indices'][1]
        assert start not in decorationsStart
        decorationsStart[start] = ('\\tweetUrl{'
                                       + escape_latex_basic(urlRec['url'])
                                       + '}{'
                                       + escape_latex_basic(urlRec['expanded_url'])
                                       + '}{'
                                       + escape_latex_basic(urlRec['display_url'])
                                       + '}{')
        assert end not in decorationsEnds
        decorationsEnds[end] = '}'
    # Media
    for mediaRec in entitiesDict.get('media', list()):
        if mediaRec['type'] == 'photo':
            url = mediaRec['media_url_https']
            filename = url.split('/')[-1].split('#')[0].split('?')[0]
            filename = tweak_filename(filename)
            if not check_file_viable(filename):
                urllib.request.urlretrieve (url, filename)
            start = mediaRec['indices'][0]
            end = mediaRec['indices'][1]
            assert start not in decorationsStart
            decorationsStart[start] = ('\\tweetPhoto{'
                                           + mediaRec['expanded_url']
                                           + '}{'
                                           + url
                                           + '}{'
                                           + escape_latex_basic(filename)
                                           + '}{')
            assert end not in decorationsEnds
            decorationsEnds[end] = '}'

# Start with user profile picture.

latexText = u''

url = tj['user']['profile_image_url_https']
url = re.sub(r"_normal(?=\.[^.]+$)", "_bigger", url)
filename = url.split('/')[-1].split('#')[0].split('?')[0]
filename = tweak_filename(filename)
if not check_file_viable(filename):
    urllib.request.urlretrieve (url, filename)
latexText += ('\\tweetUserImage{'
                  + escape_latex_basic(url)
                  + '}{'
                  + escape_latex_basic(filename)
                  + '}{'
                  + tj['user']['id_str']
                  + '}')

# User name

latexText += ('\\tweetUserName{'
                  + escape_latex_basic(tj['user']['id_str'])
                  + '}{'
                  + escape_latex_basic(tj['user']['name'])
                  + '}{'
                  + escape_latex_basic(tj['user']['screen_name'])
                  + '}')

# Verified user checkmark.

if tj['user']['verified']:
    latexText += '\\tweetUserVerified{}'

# Mark end of user name.

latexText += '\\tweetUserEnd{}';

# Add "in reply to".

in_reply_to_status_id = None
if 'in_reply_to_status_id' in tj and tj['in_reply_to_status_id'] is not None:
    in_reply_to_status_id = tj['in_reply_to_status_id']

in_reply_to_user_id = None
if 'in_reply_to_user_id' in tj and tj['in_reply_to_user_id'] is not None:
    in_reply_to_user_id = tj['in_reply_to_user_id']

in_reply_to_screen_name = None
if 'in_reply_to_screen_name' in tj and tj['in_reply_to_screen_name'] is not None:
    in_reply_to_screen_name = tj['in_reply_to_screen_name']

if (in_reply_to_status_id is not None
        and in_reply_to_user_id is not None
        and in_reply_to_screen_name is not None):
    latexText += ('\\tweetInReplyToTweet{'
                      + escape_latex_basic(str(in_reply_to_status_id))
                      + '}{'
                      + escape_latex_basic(str(in_reply_to_user_id))
                      + '}{'
                      + escape_latex_basic(in_reply_to_screen_name)
                      + '}')

# Loop over tweet's text and insert decorations for entities.

tweetText = tj['full_text']
i = 0
prev_ch = None
for i in range(0,len(tweetText)):
    ch = tweetText[i]
    if i in decorationsEnds:
        latexText += decorationsEnds[i]

    if i in decorationsStart:
        latexText += decorationsStart[i]

    if ch == '~':
        latexText += '\\char`\\~{}'
    elif ch == "\n":
        latexText += "\\hfill\\break\n\\null{}"
    elif ch == ' ' and keep_spaces and prev_ch == ch:
        latexText += '\\space{}'
    else:
        latexText += escape_latex_basic(ch)

    prev_ch = ch

if i + 1 in decorationsEnds:
    latexText += decorationsEnds[i + 1]

# Wrap emoji characters with switch to emoji containing font.

emojiRe = r"([\p{Emoticons}\p{Miscellaneous Symbols and Pictographs}\p{Transport and Map Symbols}\p{So}]+)"
emojiRe = unicode(emojiRe)

latexText = regex.sub(emojiRe, r"{\\emojifont \g<1>}", latexText, regex.V1 | regex.UNICODE)
#latexText = regex.subf(r"(\p{Emoticons}+)", "\{\\emojifont {1}\}", latexText)

# Add date with link to the tweet itself.

tweetDate = tweetDf.parse(tj['created_at'])

dateLocaleName = os.getenv('LANGUAGE', os.getenv('LC_TIME', os.getenv('LANG')))
if dateLocaleName is None:
    dateLocaleName = 'en_US'
dateLocale = Locale(dateLocaleName)

dateFormat = DateFormat.createDateInstance(DateFormat.kLong, dateLocale)
timeFormat = DateFormat.createTimeInstance(DateFormat.kLong, dateLocale)
localizedTweetDate = dateFormat.format(tweetDate)
localizedTweetTime = timeFormat.format(tweetDate)

# Wrap tweet with language settings.

langTable = {'cs': 'czech'}
latexLang = langTable.get(tj['lang'], None)
latexLangStart = ''
latexLangEnd = ''
if latexLang is not None and not use_pdflatex:
    latexLangStart = "\\text%s{" % latexLang
    latexLangEnd = "}"

latexText = (latexLangStart
                 + latexText
                 + latexLangEnd)

# Retweets count.

if 'retweet_count' in tj and tj['retweet_count'] is not None:
    latexText += ('\\tweetRetweets{'
                    + str(tj['retweet_count'])
                    + '}')

# Likes count.

if 'favorite_count' in tj and tj['favorite_count'] is not None:
    latexText += ('\\tweetFavorites{'
                    + str(tj['favorite_count'])
                    + '}')


# Add time stamp.

latexText += ('\\tweetItself{'
                  + tj['id_str']
                  + '}{'
                  + escape_latex_basic(tj['created_at'])
                  + '}{'
                  + escape_latex_basic(localizedTweetDate)
                  + '}{'
                  + escape_latex_basic(localizedTweetTime)
                  + '}')

# Tweet place.

if 'place' in tj and tj['place'] is not None:
    place = tj['place']
    map_url = urllib.parse.urlunsplit(('https', 'www.google.com', '/maps/search/',
         urllib.parse.urlencode({
             'api': 1,
             'query': (place.get('full_name', '') + ', ' + place.get('country')).encode('utf-8')
             }),
          None))
    latexText += ('\\tweetPlace{'
                      + escape_latex_basic(place.get('full_name', ''))
                      + '}{'
                      + escape_latex_basic(place.get('country'))
                      + '}{'
                      + escape_latex_basic(map_url)
                      + '}')

# Wrap into tweet environment.

if sys.version_info[0] < 3:
    html_unescape = HTMLParser.unescape
else:
    html_unescape = html.unescape

latexText = html_unescape(latexText)
latexText = ('\\begin{tweet}'
                 + latexText
                 + '\\end{tweet}')

captionText = ('\\tweetCaption{'
                   + tj['id_str']
                   + '}{'
                   + escape_latex_basic(tj['user']['name'])
                   + '}{'
                   + escape_latex_basic(tj['user']['screen_name'])
                   + '}{'
                   + escape_latex_basic(tj['created_at'])
                   + '}{'
                   + escape_latex_basic(localizedTweetDate)
                   + '}{'
                   + escape_latex_basic(localizedTweetTime)
                   + '}')

if (in_reply_to_status_id is not None
        and in_reply_to_user_id is not None
        and in_reply_to_screen_name is not None):
    captionText += ('{'
                      + escape_latex_basic(str(in_reply_to_status_id))
                      + '}{'
                      + escape_latex_basic(str(in_reply_to_user_id))
                      + '}{'
                      + escape_latex_basic(in_reply_to_screen_name)
                      + '}')
else:
    captionText += '{}{}{}'

if caption and caption_placement is CaptionPlacement.top:
    latexText = captionText + latexText
elif caption and caption_placement is CaptionPlacement.bottom:
    latexText = latexText + captionText

if sys.version_info[0] < 3:
    sys.stdout.write(latexText.encode('utf-8'))
else:
    sys.stdout.buffer.write(latexText.encode('utf-8'))
