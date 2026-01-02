"""
Hardcoded list of country and state URLs as fallback
if the website structure has changed completely
"""

# Common countries that typically have LDS statistics
COUNTRY_URLS = [
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/mexico",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/brazil",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/chile",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/argentina",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/peru",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/philippines",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/canada",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-kingdom",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/australia",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/new-zealand",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/japan",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/south-korea",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/ecuador",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/colombia",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/guatemala",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/honduras",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/el-salvador",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/nicaragua",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/costa-rica",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/panama",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/uruguay",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/paraguay",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/bolivia",
    "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/venezuela",
]

# US States
STATE_URLS = [
    f"https://newsroom.churchofjesuschrist.org/facts-and-statistics/state/{state}"
    for state in [
        "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
        "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
        "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
        "maine", "maryland", "massachusetts", "michigan", "minnesota",
        "mississippi", "missouri", "montana", "nebraska", "nevada",
        "new-hampshire", "new-jersey", "new-mexico", "new-york",
        "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon",
        "pennsylvania", "rhode-island", "south-carolina", "south-dakota",
        "tennessee", "texas", "utah", "vermont", "virginia", "washington",
        "west-virginia", "wisconsin", "wyoming", "district-of-columbia"
    ]
]
