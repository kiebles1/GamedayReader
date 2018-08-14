from datetime import date
from os import path
import urllib.request
import copy
import csv
import json
    
class baseballday(date):
    # List all the attributes from the database that we want to export in
    # one place. We can just loop through this list
    attributelist = ['away_code',
                     'away_file_code',
                     'away_name_abbrev',
                     'away_score',
                     'away_team_id',
                     'away_team_name',
                     'calendar_event_id',
                     'double_header_sw',
                     'event_time',
                     'game_nbr',
                     'game_pk',
                     'game_type',
                     'gameday_sw',
                     'group',
                     'home_code',
                     'home_file_code',
                     'home_name_abbrev',
                     'home_score',
                     'home_team_id',
                     'home_team_name',
                     'id',
                     'ind',
                     'inning',
                     'media_state',
                     'series',
                     'series_num',
                     'status',
                     'tbd_flag',
                     'top_inning',
                     'venue',
                     'venue_id']

    def output(self, outputfile):
        """Output the day's worth of games to a provided file. Currently only
        supports CSV file types but may expand to support others.
        
        Parameters:
            outputfile: an open File object to be populated with game data
        """
        
        # Check the file extension
        (ignore, ext) = path.splitext(outputfile.name)
        if ext == '.csv':
            # Add the keys as the header of the CSV and then add all the 
            # content from the list of game dictionaries
            dictwriter = csv.DictWriter(outputfile, baseballday.attributelist)
            dictwriter.writeheader()
            dictwriter.writerows(self.gameslist)
        else:
            print('File type not currently suppported.')

    def _loadjsonfromweb(self, urlstring):
        # Connec to the MLB games database and download the JSON. Use the 
        # object hook to process the JSON objects as they are parsed
        try:
            with urllib.request.urlopen(urlstring) as webresponse:
                json.loads(webresponse.read(), object_hook = self._new_game)
        except urllib.error.URLError:
            print('Error connecting to ' + urlstring + '\n')
            exit()
        
        self._stripgamedict()
            
    def _stripgamedict(self):
        # Create a list of keys that are in the dictionary to get rid of 
        # any we don't want. Because we need a deep copy of the keys list and 
        # Python's deep copy method doesn't work with key lists, we need
        # to loop through the keys and append them on the end of a new list. 
        # This is necessary because when we try to output the dictionaries
        # to a CSV, the writer object expects the list of keys
        # (our attributes list) to line up exactly with the keys in the
        # dictionaries
        keyslist = []
        for key in self.gameslist[0].keys():
            keyslist.append(key)
            
        for key in keyslist:
            if key not in baseballday.attributelist:
                for dict in self.gameslist:
                    del dict[key]
    
    def _new_game(self, dct):
        # This is our custom handler for parsing JSON objects. We just want
        # to see if the game_media key is present, indicating that this is
        # a game object, and if so store off the game info.
        if 'game_media' in dct:
            self.gameslist.append(dct)
            
    def _pulldateinfo(self):
        # Use the user provided date to create our URL for getting the data.
        urlbase = 'https://gd2.mlb.com/components/game/mlb/'
        yearstring = self.strftime("%Y")
        daystring = self.strftime("%d")
        monthstring = self.strftime("%m")
        urlstring = (urlbase + "year_" + yearstring + "/month_" + monthstring + 
                    "/day_" + daystring  + "/grid.json")
        self._loadjsonfromweb(urlstring)
            
    def __init__(self, year, month, day):
        """ Initialize a baseball day object, which extends a Python date
        object to facilitate some handling of the date and it's format.
        
        Parameters:
            year: The 4-digit year of the date you are requesting
            month: The 2-digit (leading zero) month of the date you are
                   requesting
            day: The 2-digit (leading zero) day of the month of the day you
                 are requesting
        """
        self.gameslist = []
        self._pulldateinfo()
        
if __name__ == "__main__":
    """Execute the program to download MLB game date and populate a CSV. Pass
    '-h' flag for help. Command line arguments are, in order:
        <ISO Date> <CSV Output File>.
    """
    import sys
    
    # Store off our help string since we want to output it in more than one
    # condition
    help = 'This program gets the data from a given day in MLB ' \
           'history and stores it into a CSV file. The format to run ' \
           'the file is "py GameData.py <Date> <CSV Output File>". ' \
           'The date must be provided in ISO format (YYYY-MM-DD).'
    
    try:
        # If the user is passing too much, give them help
        if (len(sys.argv) > 3) or (sys.argv[1] == "-h"):
            if(len(sys.argv) > 3):
                print('Too many arguments\n')
            print(help)
            exit()
        else:
            # Create a new day of baseball for the user-provided date, then
            # write it to the user-provided CSV file
            day = baseballday.fromisoformat(sys.argv[1])
            with open(path.realpath(sys.argv[2]), 'w', newline='') as f:
                day.output(f)
    # If the user didn't give enough arguments, give them help. We could
    # handle the IO exception for an invalid file too, but the standard
    # exception outputs for this error are just as useful as anything we could
    # do here, plus the program has to quit anyways now.
    except IndexError:
        print('Too few arguments\n')
        print(help)
        