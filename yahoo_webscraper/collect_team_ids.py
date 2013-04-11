"""
Create a dictionary of Team Names and internal id's from rivals.yahoo.com;

The Yahoo! HTML is computer-generated, but can you can infer team id's
from relative URL's. For example, the Albany Great Danes' URL is
http://rivals.yahoo.com/ncaab/teams/aca

So, if we scrape the HTML from the (general) teams page, and use the
search pattern /ncaab/teams/xyz inside <a> tags, we can identify what
id Yahoo! has associate with any particular team.

This correspondence is outputted in the dictionary, team_ids.

NOTE: Yahoo! doesn't always use conventional names for teams. For example,
George Washington U is recognized as 'Geo. Washington'.  
"""

from bs4 import BeautifulSoup
import re 
import mechanize

br = mechanize.Browser()
teams_page_html = br.open("http://rivals.yahoo.com/ncaa/basketball/teams").get_data()
tag_soup = BeautifulSoup(teams_page_html)

team_ids = dict()

regex_pattern = re.compile('/ncaab/teams/[a-z]{3}') # search pattern for anchor tags

for tag in tag_soup.find_all('a',href=regex_pattern):
    # bs4 converts &nbsp; into u'\xa0'; need to strip that out, when its present and replace with ' '
    team_name = tag.text.replace(u'\xa0',' ').encode('utf-8')
    team_id = tag.get('href').split('/')[3]
    team_ids[team_name] = team_id

