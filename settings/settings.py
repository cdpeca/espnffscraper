" Set variables for accessing your private league "

#SWID COOKIE
swid = None

#LONG ESPN S2 COOKIE
espn_s2 = None

# ID of your league <you must change this setting here or in settings_local.py or program will fail>
league_id = 1234567

# Year of your league
year = 2020

# Is league open to public
league_open_to_public = True

# Set the sport for the ESPN fantasy league
sport='nfl'

# Override variables from settings/settings_local.py if this module exists
try:
    from settings.settings_local import *
except ImportError:
    pass

