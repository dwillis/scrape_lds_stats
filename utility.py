from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import json

def get_links(base_link):
    '''Uses base link to get every state or country link on page
    '''
    res = requests.get(base_link)
    soup = BeautifulSoup(res.content, "html.parser")

    links = []
    base_str = "https://newsroom.churchofjesuschrist.org"
    
    # Try original method first (with data-code attribute)
    for link in soup.find_all("li"):
        if link.select("a") and link.select("a")[0].has_attr("data-code"):
            tmp_link = link.select("a")[0].get("href")
            if len(tmp_link)>10:
                links.append(base_str + tmp_link)
    
    # If no links found, try alternative method (all links with facts-and-statistics/country or state in href)
    if not links:
        print("Warning: No links found with data-code attribute, trying alternative selector...")
        all_links = soup.find_all("a", href=True)
        for a in all_links:
            href = a.get("href", "")
            # Look for country or state links
            if ("/facts-and-statistics/country/" in href or "/facts-and-statistics/state/" in href):
                if href.startswith("http"):
                    links.append(href)
                else:
                    links.append(base_str + href)
    
    # If still no links, try to find JSON data in script tags (for JavaScript-rendered content)
    if not links:
        print("Warning: No links found in HTML, checking for JSON data in script tags...")
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                try:
                    # Look for JSON that might contain country/state data
                    script_text = script.string.strip()
                    if script_text.startswith('{') or 'countries' in script_text.lower() or 'states' in script_text.lower():
                        # Try to extract JSON
                        data = json.loads(script_text)
                        # Look for country or state information in the JSON
                        links_from_json = _extract_links_from_json(data, base_str)
                        if links_from_json:
                            links.extend(links_from_json)
                            break
                except (json.JSONDecodeError, AttributeError):
                    continue
    
    # Last resort: Try Selenium for JavaScript-rendered content
    if not links:
        print("Warning: No links found via static methods, trying Selenium (this may take a moment)...")
        try:
            links = _get_links_with_selenium(base_link, base_str)
        except Exception as e:
            print(f"Selenium attempt failed: {e}")
    
    # Final fallback: Use hardcoded URLs if this is a known base URL
    if not links:
        print("Warning: All dynamic methods failed, using hardcoded fallback URLs...")
        try:
            from fallback_urls import COUNTRY_URLS, STATE_URLS
            if "facts-and-statistics/country/united-states" in base_link:
                links = STATE_URLS
                print(f"Using {len(links)} hardcoded state URLs")
            elif "facts-and-statistics" in base_link:
                links = COUNTRY_URLS
                print(f"Using {len(links)} hardcoded country URLs")
        except ImportError:
            print("Could not import fallback URLs")
    
    print(f"Found {len(links)} links from {base_link}")
    return links

def _get_links_with_selenium(url, base_str):
    '''Use Selenium to get links from JavaScript-rendered content'''
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    links = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for content to load (wait for links to appear)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
        
        # Give it a moment for JavaScript to fully execute
        import time
        time.sleep(2)
        
        # Get the page source after JavaScript execution
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Try all methods again with the rendered HTML
        all_links = soup.find_all("a", href=True)
        for a in all_links:
            href = a.get("href", "")
            if ("/facts-and-statistics/country/" in href or "/facts-and-statistics/state/" in href):
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    links.append(base_str + href)
        
        # Also try data-code method
        for li in soup.find_all("li"):
            anchors = li.select("a")
            if anchors and anchors[0].has_attr("data-code"):
                tmp_link = anchors[0].get("href")
                if tmp_link and len(tmp_link) > 10:
                    if tmp_link.startswith("http"):
                        links.append(tmp_link)
                    elif tmp_link.startswith("/"):
                        links.append(base_str + tmp_link)
        
    finally:
        if driver:
            driver.quit()
    
    return list(set(links))  # Remove duplicates

def _extract_links_from_json(data, base_str):
    '''Recursively search JSON data for country/state links'''
    links = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Look for URL fields
            if isinstance(value, str) and ('/facts-and-statistics/country/' in value or '/facts-and-statistics/state/' in value):
                if value.startswith('http'):
                    links.append(value)
                elif value.startswith('/'):
                    links.append(base_str + value)
            # Recurse into nested structures
            elif isinstance(value, (dict, list)):
                links.extend(_extract_links_from_json(value, base_str))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                links.extend(_extract_links_from_json(item, base_str))
            elif isinstance(item, str) and ('/facts-and-statistics/country/' in item or '/facts-and-statistics/state/' in item):
                if item.startswith('http'):
                    links.append(item)
                elif item.startswith('/'):
                    links.append(base_str + item)
    
    return links

def get_data(link):
    '''Given a link, parses text and return dictionary of data
    '''
    try:
        res = requests.get(link)
        soup = BeautifulSoup(res.content, "html.parser")
        data_string = _get_data_string(soup)

        data_dict = {}

        name = re.subn(r' - .+',"",soup.title.text)[0] if soup.title else "Unknown"
        print(name)

        data_dict['Name'] = name

        metrics = [
            'TotalChurchMembership',
            'Stakes',
            'Congregations',
            'Wards',
            'Branches',
            'FamilySearchCenters',
            'Temples',
            'Missions',
            'Districts'
        ]

        for metric in metrics:
            data_dict[metric] = \
                _get_data_in_string(data_string, metric)

        return data_dict
    except Exception as e:
        print(f"Error scraping {link}: {e}")
        return None


def _get_data_string(soup):
    '''Uses CSS selectors to parse text into manageable piece
    '''
    text = []
    
    # Try original selectors first
    try:
        #Missions
        missions_elem = soup.select(".stat-line.one-fifth")
        if missions_elem:
            text1 = missions_elem[0].text
            text1 = text1.split()
        else:
            text1 = []

        #Everything else
        graph_elem = soup.select(".stat-line.w-graph")
        if graph_elem:
            text2 = graph_elem[0].text
            text2 = re.subn(
                pattern = " ", 
                repl = "", 
                string = text2
            )[0]
            text2 = text2.split()
        else:
            text2 = []

        text = text1 + text2
    except Exception as e:
        print(f"Warning: Original selectors failed: {e}")
    
    # If original selectors didn't work, try alternative approaches
    if not text:
        try:
            # Try just .stat-line
            all_stat_lines = soup.select(".stat-line")
            for elem in all_stat_lines:
                elem_text = re.subn(pattern = " ", repl = "", string = elem.text)[0]
                text.extend(elem_text.split())
        except:
            pass
    
    # Last resort: look for any element with stat-related classes
    if not text:
        try:
            stats = soup.find_all(class_=lambda x: x and 'stat' in str(x).lower())
            for elem in stats:
                elem_text = re.subn(pattern = " ", repl = "", string = elem.text)[0]
                text.extend(elem_text.split())
        except:
            pass
    
    return text

def _get_data_in_string(string, name):
    '''given a metric name, finds data for that name
    '''
    if name in string:
        idx = string.index(name) - 1
        data = re.subn(",", "", string[idx])[0]
        if data.isdigit():
            return int(data)
        else:
            return 0
    return 0

def get_temple_data():

    try: 
        base_link = "https://church-of-jesus-christ-facts.net/temple5/"

        res = requests.get(base_link)
        soup = BeautifulSoup(res.content, "html.parser")

        to_it = soup.select('pre')[1].text.replace("\xa0"," ").split('\r\n')
        to_it = [x for x in to_it if len(x)>0]

        pattern = re.compile(r"\s\s+")

        col_names = pattern.split(to_it[0])
        col_names = [x for x in col_names if len(x)>0]

        df = []
        for row in to_it[1:]:
            row = pattern.split(row)
            row = [x for x in row if len(x)>0]
            tmp_dict = {
                col_names[0] : row[0],
                col_names[1] : row[1],
                col_names[2] : row[2],
                col_names[3] : row[3],
                col_names[4] : row[4],
            }
            if len(row)>=6:
                tmp_dict[col_names[5]] = row[5]
            else:
                tmp_dict[col_names[5]] = ''
            df.append(tmp_dict)
            
        t_site_1 = pd.DataFrame(df) \
            .rename(columns = {'Name and location':'Temple'}) \
            .assign(Temple = lambda x:x.Temple.apply(_clean_names))
    except:
        raise Exception("church-of-jesus-christ-facts failed.")

    base_link = "https://churchofjesuschristtemples.org/statistics/dimensions/"
    res = requests.get(base_link)
    soup = BeautifulSoup(res.content, "html.parser")
    to_it = soup.select("tr")

    df = []
    for row in to_it[1:]:
        row = row.text.split("\n")
        row = [x for x in row if len(x)>0]
        tmp_dict = {
            'Temple' : row[0],
            'Instruction_Rooms' : row[1],
            'Sealing_Rooms' : row[2],
            'Baptismal_Fonts' : row[3],
            'Square_Footage' : row[4],
            'Acreage': row[5]
        }
        df.append(tmp_dict)

    t_site_2 = pd.DataFrame(df) \
        .assign(Temple = lambda x:x.Temple.apply(_clean_names))

    base_link = "https://churchofjesuschristtemples.org/statistics/features/"
    res = requests.get(base_link)
    soup = BeautifulSoup(res.content, "html.parser")
    to_it = soup.select("tr[class = 'clickable-row']")

    df = []
    for row in to_it:
        row = row.text.split("\n")
        row = [x for x in row if len(x)>0]
        tmp_dict = {
            'Temple' : row[0],
            'Num_Spires' : row[1],
            'Spire_Attached' : row[2],
            'Angel_Moroni' : row[3]
        }
        df.append(tmp_dict)

    t_site_3 = pd.DataFrame(df) \
        .assign(Temple = lambda x:x.Temple.apply(_clean_names))

    t_site_2 = pd.merge(t_site_3, t_site_2, how='inner',on='Temple')

    data = pd.merge(t_site_1, t_site_2, how='inner',on='Temple')

    return data

def _clean_names(name):
    return name.lower().strip().replace(".","") \
        .replace("á", "a") \
        .replace('é', 'e') \
        .replace('ó', 'o') \
        .replace('é', 'e') \
        .replace("ã", "a") \
        .replace("í", "i") \
        .replace("seoul korea temple", "seoul south korea temple") \
        .replace("mt timpanogos utah temple", "mount timpanogos utah temple") \
        .replace("bogota dc colombia temple", "bogota colombia temple") \
        .replace("trujillo mexico temple", "trujillo peru temple") \
        .replace("caracas df venezuela temple", "caracas venezuela temple") \
        .replace("kinshasa dem republic of congo temple", "kinshasa democratic republic of the congo temple") \
        .replace("merida yucatan mexico temple", "merida mexico temple") \
        .replace("mexico city df mexico temple", "mexico city mexico temple") \
        .replace("calgary alberta temple", "calgary canada temple")
