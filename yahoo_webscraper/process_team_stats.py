from bs4 import BeautifulSoup
import re 
import mechanize
import csv
from collect_team_ids import team_names,team_ids

def scrape_schedule_table(url="http://rivals.yahoo.com/ncaa/basketball/teams/aca/stats"):
    """ Doc string
    """
    
    br = mechanize.Browser()
    stat_page_html = br.open(url).get_data()
    
    tag_soup = BeautifulSoup(stat_page_html)
    
    table_header = ['Date','Opponent','Result','Score','Postseason']
    team_schedule = [table_header]

def scrape_stat_table(url):
    """ Recreates the stats table found at input, url, as a list of lists. 
        
        Input:
            url - assumed to be of the form rivals.yahoo.com/ncaab/teams/XYZ/stats
        
        Output:
            team_stats - a list whose elements are lists representeing rows of the 
                         stats table found at the URL. The first list is the table
                         header
    """
    
    br = mechanize.Browser()
    stat_page_html = br.open(url).get_data()
    
    tag_soup = BeautifulSoup(stat_page_html)
    
    team_stats = list() # initialize empty table
    
    # create header
    header_list = list()
    
    for td in tag_soup.find('tr','ysptblthbody1').find_all('td'):
        ''' Header row-entry is a bit weird; First three stat titles
            are contained in the <td> tags, however later stats are 
            surrounded by <a>'s linking to their explanation. Also,
            there are auxiliary, empty <td>'s set up for spacing purposes.
            We don't care about those, so we'll filter on the existence of
            a class attribute, or an <a>-child-tag to extract titles
        '''
        
        if td.has_attr('class'):
            stat_title = td.text.replace(u'\xa0','').encode('utf-8')
            header_list.append(stat_title)
        elif td.find('a'):
            stat_title = td.find('a').text.replace(u'\xa0','').encode('utf-8')
            header_list.append(stat_title)
        
    
    team_stats.append(header_list)
    
    # populate the rest of the table
    for row in tag_soup.find_all('tr', re.compile("ysprow[12]")):
        ''' Filter on row elements whose class is either ysprow1 or ysprow2;
            Then, filter on column elements whose class is yspscores, to avoid
            picking up the auxiliary, empty <td>'s generated for aesthetic.        
        '''
        tmp_row = list()
        for col_entry in row.find_all('td', "yspscores"):
            tmp_row.append(col_entry.text.replace(u'\xa0','').encode('utf-8'))
        team_stats.append(tmp_row)
        
    return team_stats

def export_stat_table_as_csv(table,filename):#url="http://rivals.yahoo.com/ncaa/basketball/teams/aca/stats"):
    with open(filename,'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)
        csvfile.close()
    
def scrape_and_export_team_stats(url):
    """ Scrapes the team statistics table from the provided URL and exports as a csv
    
        Input: 
            url - points to any Yahoo! NCAA men's basketball team's stat page
        
        Output:
            .csv file named according to "year_of_season_of_stats-team_name.csv" 
    """
    
    table = scrape_stat_table(url)
    
    ## make filename based on format: year_of_query-team_name.csv
    year_match = re.search('(?<=year=)(20[01][0-9])',url) # may be empty
    
    if year_match: # if the regex returns a match
        year = year_match.group(0)
    else: # user is querying for current season
        year = '2012'
        
    team_id = re.search('(?<=teams/)([a-z]{3})',url).group(0) # should NOT be empty
    team_name = team_names[team_id].replace(' ','_') # make team name filename-friendly
    filename = '-'.join([year,team_name])
    filename = '.'.join([filename,'csv'])
    
    export_stat_table_as_csv(table,filename)
    
def yahoo_stat_url_for_team(team_name,year=2012):
    if team_ids.has_key(team_name) and year in range(2001,2013):
        team_id = team_ids[team_name]
        suffix = ''.join(["stats?year=",str(year)])
        url = "/".join(["http://rivals.yahoo.com/ncaab/teams",team_id,suffix])
    else: # throw an error!
        url = "bad.url.com"
    
    return url

def converted_date(date_string):
    """ expect a string like "Fri, Nov 3, 2004".
        want to output 2004-11-3
    """ 
    month_regex = ".*?(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    month_dict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

    
    try:
        year = re.match(".*?(?P<year>[0-2][0-9]{3})",date_string).group("year")
        month = re.match(month_regex,date_string).group("month")
        numerical_month = str(month_dict[month])
        numerical_day_regex = ''.join([".*?(?<=",month,"\s)(?P<day_num>[0-9]{1,2}?)"])
        numerical_day = re.match(numerical_day_regex,date_string).group("day_num")
        reformated_date = "-".join([year,numerical_month,numerical_day])
        return reformated_date
    except (AttributeError,KeyError) as e:
        print("Improperly formed date string!")
        

if __name__ == "__main__" :
#    ### test against 2004 season for South Carolina Upstate Spartans:
#    url = "http://rivals.yahoo.com/ncaa/basketball/teams/sec/stats?year=2004"
#    
#    #scrape_and_export_team_stats(url)
#    print yahoo_stat_url_for_team('N. Mexico St.',2004)

#<tr class="ysprow1" valign="top"><td height="18">&nbsp;</td><td nowrap>Fri, Nov  9</td>
#    <td><a href=/ncaab/teams/dav>Duquesne</a></td>
#    <td><a href=/ncaab/recap?gid=201211091176>W 69-66</a></td>
    
    print converted_date("Fri, November 3 2012")
    
    url = "http://rivals.yahoo.com/ncaa/basketball/teams/aca/schedule?y=2004"
    
    br = mechanize.Browser()
    schedule_page_html = br.open(url).get_data()
    
    tag_soup = BeautifulSoup(schedule_page_html)
    
    table_header = ['Date','Opponent','Location','Result','Score','Postseason']
    team_schedule = [table_header]
    
    for schedule_row in tag_soup.find_all('tr', re.compile('ysprow[12]')):
        """ the easiest way to do this is the straight-forward
            brute force way; col's 4,5,6 are useless to us
        """
        td_list = schedule_row.find_all('td')
        col_indx = range(0,len(td_list))
        
        cols = {}
        
        for (col_entry,col_num) in zip(td_list,col_indx):
                print (col_entry,col_num)
#            
# col-2 : convert date;
# col-3: if "at" exists, turn location value to "A"
#        extract opponent name from <a>.text
# col-4: take first character (W|L) as value for result
#        take \s(?P<result>[0-9]{1,3}?-[0-9]{1,3}?) as score
    