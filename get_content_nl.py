import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
from googletrans import Translator
from fuzzywuzzy.fuzz import token_sort_ratio

df_content_nl = pd.DataFrame()
all_website_dates = []  # list for all dates
matched_indices_change = [] # needed to avoid matching the same entry twice
date_index = 0 # counter to correctly label the headers of the df with the appropriate
timeout = 0 # counter to see how many iterations we already did -> one iteration = 1 day

eu_countries_dutch = [
    "Albanië",
    "Andorra",
    "Armenië",
    "Oostenrijk",
    "Azerbeidzjan",
    "België",
    "Bosnië en Herzegovina",
    "Bulgarije",
    "Kroatië",
    "Cyprus",
    "Tsjechië",
    "Denemarken",
    "Estland",
    "Finland",
    "Frankrijk",
    "Georgië",
    "Duitsland",
    "Griekenland",
    "Hongarije",
    "IJsland",
    "Ierland",
    "Italië",
    "Kazachstan",
    "Letland",
    "Liechtenstein",
    "Litouwen",
    "Luxemburg",
    "Malta",
    "Moldavië",
    "Monaco",
    "Montenegro",
    "Nederland",
    "Noord-Macedonië",
    "Noorwegen",
    "Polen",
    "Portugal",
    "Roemenië",
    "Rusland",
    "San Marino",
    "Servië",
    "Slowakije",
    "Slovenië",
    "Spanje",
    "Zweden",
    "Zwitserland",
    "Turkije",
    "Oekraïne",
    "Verenigd Koninkrijk"
]

def main():
    global date_index
    global df_content_nl

    max_day = 31
    max_month = 1200
    variable_urlpart = 20230412 # first snapshot it at 20230412 
    while variable_urlpart < 20240202: # put the TIMEFRAME your interested here 
        if variable_urlpart % 100 < max_day: # day counter
            variable_urlpart += 1 # adds one day
            try:
                website_date, uniquedate_url = scrapedate(str(variable_urlpart)) # returns website date and the url of that date
            except TypeError: # filter out redirects from Wayback (some urls are redirects to other urls)
                pass
            else:
                if website_date: # include if statement to ensure that it only appends to the list if it finds something ( a date that includes a "tuesday" eg to ensure it writes only then to the list)
                    if website_date not in all_website_dates:
                        all_website_dates.append(website_date) # add date to list for referencing and creating unique headers
                        entire_entries = scrape_list(uniquedate_url)
                        amount, weapon = reshuffle_items(entire_entries)
                        # get dimensions and column names of the current entries -> needed to have the committed and delivered df equal in length in the end
                        max_length = set_dimensions(amount, weapon, df_content_nl)
                        # update the dataframe with the new data, ensuring equal length of both dfs
                        write_to_df_content_nl(amount, weapon, max_length)
                        # clean excess entries
                        df_content_nl.apply(cleanup, axis=1, df_nl = df_content_nl)
                        date_index += 1

        elif variable_urlpart % 10000 < max_month: # month counter
            variable_urlpart += 70 # adds one month (100) and substracts 30 days
            try:
                website_date, uniquedate_url = scrapedate(str(variable_urlpart))
            except TypeError:
                pass
            else:
                if website_date:
                    if (website_date) not in all_website_dates:
                        all_website_dates.append(website_date)
                        entire_entries = scrape_list(uniquedate_url)
                        amount, weapon = reshuffle_items(entire_entries)
                        max_length = set_dimensions(amount, weapon, df_content_nl)
                        write_to_df_content_nl(amount, weapon, max_length)
                        df_content_nl.apply(cleanup, axis=1, df_nl = df_content_nl)
                        date_index += 1

        else:
            variable_urlpart += 8870 # year counter, adds one year (10000) and substracts 11 months (1100) and 30 days to get back to the 01.01.YYYY
            try:
                website_date, uniquedate_url = scrapedate(str(variable_urlpart))
            except TypeError:
                pass
            else:
                if website_date:
                    if (website_date) not in all_website_dates:
                        all_website_dates.append(website_date)
                        entire_entries = scrape_list(uniquedate_url)
                        amount, weapon = reshuffle_items(entire_entries)
                        max_length = set_dimensions(amount, weapon, df_content_nl)
                        write_to_df_content_nl(amount, weapon, max_length)
                        df_content_nl.apply(cleanup, axis=1, df_nl = df_content_nl)
                        date_index += 1

    # converts all integers that are currently still saved as strings to int
    df_content_nl = df_content_nl.map(try_convert_to_int)
    
    # translate description column to english using google translate API
    for i in range(len(all_website_dates)):
        print(f"translated {i + 1} snapshots")
        df_content_nl[f"{all_website_dates[i]} Description"] = df_content_nl[f"{all_website_dates[i]} Description"].apply(translate_text)
    # write to one excel file
    with pd.ExcelWriter("military_output_nl.xlsx") as writer:
        df_content_nl.to_excel(writer, sheet_name="NL", index=False, freeze_panes=(1,0))

def scrapedate(variable_url_part):
    global timeout
    # get HTML content
    url = f"https://web.archive.org/web/{variable_url_part}999999/https://www.defensie.nl/onderwerpen/oostflank-navo-gebied/militaire-steun-aan-oekraine"
    
    response = requests.get(url)
    html_content_full = response.text
    html_lines_full = html_content_full.splitlines()

    # Search for the line containing the date that the page was last published
    target_string = '"last_published"'

    # enumerates until the lines variable reaches the word "handover", then saves the respective line as critical line
    for line_number, line in enumerate(html_lines_full, start=1):
        if target_string in line: #if not repeat the loop
            critical_line=line_number - 1 # to correctly retrieve the line in html code
            break #for efficiency to stop the loop once it found the word

    line_of_interest = html_lines_full[critical_line]
    # now extract the date that the website was last published (maxsplit = 1)
    html_date = line_of_interest.split(":", 1)[1].strip().replace('"','')
    year = html_date[:4]
    month = html_date[5:7]
    day = html_date[8:10]
    complete_date = f"{day}.{month}.{year}"

    timeout += 1
    sleep(15) # sleep to not get kicked from requesting
    print(f"covered {timeout} days, currently at {variable_url_part}")

    return complete_date, url

def scrape_list(unique_url):
    
    # Scraping logic
    response = requests.get(unique_url)
    html_content_full = response.text

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content_full, 'html.parser')

    # Find the first <ul> tag and get its contents
    first_ul = soup.find('ul')
    ul_content = str(first_ul)
    # strip away HTML tags
    ul_content = ul_content.replace("<ul>", "").replace("</ul>", "").replace("\xa0"," ").replace("“","").replace("”","").replace("&nbsp;","").strip()

    # if the header is Munitie, turn all " en" to "," for that categorie and append the word munitie in front of every comma
    # Use regular expressions to find <li> blocks containing <strong>Munitie</strong> and apply the replacement function (flags=re.DOTALL ensures that the regex engine matches the entire block of <li> containing <strong>Munitie</strong>, regardless of whether it spans multiple lines)
    modified_html = re.sub(r'<li>(?=(?:(?!<\/li>).)*?<strong>Munitie<\/strong>).*?<\/li>', replace_ammo, ul_content, flags=re.DOTALL).replace("munitie munitie", "munitie")
    modified_html2 = re.sub(r'<li>(?=(?:(?!<\/li>).)*?<strong>Reservedelen<\/strong>).*?<\/li>', replace_spare_parts, modified_html, flags=re.DOTALL)

    # Define the patterns to search for
    pattern1 = r'.*?</strong><br/>.*'
    pattern2 = r'.*?</strong> <br/>.*'
    pattern3 = r'.*?</strong> <br />.*'

    # Use re.sub() to replace lines containing the patterns with an empty string
    cleaned_string = re.sub(pattern1, '', modified_html2)
    cleaned_string = re.sub(pattern2, '', cleaned_string)
    cleaned_string = re.sub(pattern3, '', cleaned_string)

    # Do more stripping, for better formating later on
    cleaned_string = cleaned_string.replace("Viking-rupsvoertuigen.", "Viking-rupsvoertuigen,").replace(", zoals"," zoals").replace("Zoals ", "").replace("helderheidsversterkers en", "helderheidsversterkers +").replace("ten minste ", "").replace("in totaal ","").replace("berging en ", "berging + ").replace("(Mobiele) ", "Mobiele ").replace("Computers, datasystemen en toebehoren", "Computers + datasystemen + toebehoren")
    # replacing "en" by "+" if it is surrounded by any country from eu_countries
    pattern_en = r"\b(" + "|".join(eu_countries_dutch) + r")\b\s+en\s+\b(" + "|".join(eu_countries_dutch) + r")\b"
    cleaned_string = re.sub(pattern_en, r'\1 + \2', cleaned_string)

    # remove language tags
    cleaned_string = re.sub(r'<span.*?>', '', cleaned_string)
    cleaned_string = re.sub(r'</span>', '', cleaned_string)

    # Parse cleaned_string as HTML using BeautifulSoup to remove HTML tags and get text
    cleaned_soup = BeautifulSoup(cleaned_string, 'html.parser')
    cleaned_text = cleaned_soup.get_text(separator='\n', strip=True)

    # remove full stops at end of sentences, some weird "and" statement, concatenate hyphen words that have a \n
    cleaned_text = cleaned_text.replace(".\n","\n").replace("- en ","").replace("-\n","-").replace("\n-","-")

    # convert " .\d" to " #\d" so we can then remove all full stops and re-replace the # with fullstop 
    cleaned_text = re.sub(r' \.(\d)', r' #\1', cleaned_text)
    cleaned_text = cleaned_text.replace(".", "").replace("#",".")
    
    # add "stuks" bracket in case it is missing -> (23) = (23 stuks)
    cleaned_text = re.sub(r"\((\d+)\)", r"(\1 stuks)", cleaned_text)

    # also remove unwanted next lines
    cleaned_text = re.sub(r'(?<!\))\n\(', ' (', cleaned_text)

    # after making sure that we can safely replace " en " by ", " (and then by \n) we can split items at each \n to get an individual list.
    cleaned_text = cleaned_text.replace(" en ", ", ").replace(", ", "\n")
    # Remove empty lines
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)

    cleanedlist = cleaned_text.strip().split("\n")

    return cleanedlist

def cleanup(row, df_nl):
    global date_index
    if df_nl.at[row.name, f"{all_website_dates[date_index]} Description"] == "":
        df_nl.at[row.name, f"{all_website_dates[date_index]} Last Occurrence [Dummy]"] = ""
        df_nl.at[row.name, f"{all_website_dates[date_index]}"] = ""
        df_nl.at[row.name, f"{all_website_dates[date_index]} HUMAN CHECK"] = ""
    try:
        if df_nl.at[row.name, f"{all_website_dates[date_index - 1]} Description"] == "":
            df_nl.at[row.name, f"{all_website_dates[date_index - 1]} Last Occurrence [Dummy]"] = ""
            df_nl.at[row.name, f"{all_website_dates[date_index - 1]}"] = ""
    except IndexError:
        pass
    try:
        if df_nl.at[row.name, f"{all_website_dates[date_index - 2]} Description"] == "":
            df_nl.at[row.name, f"{all_website_dates[date_index - 2]} Last Occurrence [Dummy]"] = ""
            df_nl.at[row.name, f"{all_website_dates[date_index - 2]}"] = ""
    except IndexError:
        pass

def set_dimensions(a, w, df):
    max_length_local = max(len(a), len(w), len(df))
    return max_length_local

def reshuffle_items(list):
    # group one is the digit only, group two is the remainder
    pattern_starts_with_int = re.compile(r'^(\d+)\s(.*)')
    # make three groups, group 1/3 is text surrounding the integers, group 2 is integer
    pattern_int_stuk = re.compile(r"^(.*?)(\d+)\s*(stuks.*)")
    # Initialize an empty list to store the items that match the pattern
    amounts = []
    description = []

    # Iterate over each item in the list
    for item in list:
        # first try to see if we have numbers in front of the entry (e.g. "2 guns") 
        match = pattern_starts_with_int.match(item)
        if match:
            # If there's a match, append the digit part to digits_list and the rest to rest_list
            amounts.append(match.group(1))
            description.append(match.group(2))
        else: # now check if we have e.g. "good guns (3 stuks) from Netherlands"
            match = pattern_int_stuk.search(item)
            if match:
                before_number = match.group(1)
                rest_of_text = match.group(3)
                description.append(before_number + rest_of_text)
                amounts.append(match.group(2))
            else: # mark undisclosed if no integer is found
                amounts.append("undisclosed")
                description.append(item)

    for i in range(len(description)):
        description[i] = description[i].replace(" (stuks)", "").replace(" stuks", "")

    return amounts, description

def try_convert_to_int(value): # converts all int to int iff possible
    try:
        return int(value)
    except (ValueError, TypeError):
        return value

def strip_target_weapon(tw):
    pass # included just in case we need it

def strip_dataframe(df):
    pass # included just in case we need it

def calculate_change(row, df_nl):
    global date_index # date_index is new date, date_index -1 is baseline
    best_match_score = -1  # start best match score (fuzzy.ratio ranges from [0-100] so -1 ensures that score/index will always be updated (bit arbitrary could also be set to 0))
    best_match_index = -1  # start index of best match 

    target_weapon = row[f"{all_website_dates[date_index]} Description"] # define target key that will be used to match entries
    stripped_target_weapon = target_weapon # strip_target_weapon(target_weapon) # update later if needed
    stripped_df = df_nl # strip_dataframe(df_nl) # update later if needed

    new_delivered_value = row[f"{all_website_dates[date_index]} Amount"]

    for index, baseline_weapon in enumerate(stripped_df[f"{all_website_dates[date_index - 1]} Description"]): # iterate through all baseline_weapons and match to new_weapon
        if index not in matched_indices_change:
            similarity_score = token_sort_ratio(baseline_weapon.lower(), stripped_target_weapon.lower()) # create similarity score based on baseline/new weapon irrespectively of word order (Levenshtein distance)
            if similarity_score > best_match_score:
                best_match_score = similarity_score
                best_match_index = index

    if best_match_score > 80:  # if the current target_value is matched with a baseline entry with >75%, we retrieve the baseline_amount of that weapon 
        if best_match_score == 100: # only "take away" the matches that are 100% exact, not for fuzzy matching
            matched_indices_change.append(best_match_index)  # add the matched index to the list
        baseline_value = df_nl.at[best_match_index, f"{all_website_dates[date_index - 1]} Amount"]
        try:
            change = int(new_delivered_value) - int(baseline_value) # then calculate the difference btw new and baseline amount 
            if change == 0:
                change = "no change" # for clarity, could also leave as 0
        except ValueError:
            try: # if one amount goes from undisclosed to int, we capture the now disclosed amount
                change = int(new_delivered_value)        
            except ValueError: # in case of two undisclosed amounts
                if new_delivered_value != "":
                    change = "no change"
                else: # not necessary, leave in for good measure, cleanup could take care of it
                    change = ""
        if new_delivered_value != "": # not necessary, leave in for good measure, cleanup could take care of it
            df_nl.at[row.name, f"{all_website_dates[date_index]} New Item [Dummy]"] = "No"
        
    else: # if match threshold is not reached, differentiate between new entries and empty cells
        if target_weapon != "":
            df_nl.at[row.name, f"{all_website_dates[date_index]} New Item [Dummy]"] = "Yes"
            change = new_delivered_value # if we have a new entry, mark change as total of what is NEW
        elif target_weapon == "":
            change = "" # if the new_weapon entry is empty, just append an empty string

    # update the new_change column directly in the function
    df_nl.at[row.name, f"{all_website_dates[date_index]} Change"] = change

    # Add human check column for person checking entries (marks all New Items, non perfect matches and strange values for change as "CHECK")
    try:
        change = int(change)
    except ValueError:
        if best_match_score != 100:
            df_nl.at[row.name, f"{all_website_dates[date_index]} HUMAN CHECK"] = "CHECK"
        else:
            df_nl.at[row.name, f"{all_website_dates[date_index]} HUMAN CHECK"] = "No"
    else:
        if best_match_score != 100 or change > 1000 or change < 0:
            df_nl.at[row.name, f"{all_website_dates[date_index]} HUMAN CHECK"] = "CHECK"
        else:
            df_nl.at[row.name, f"{all_website_dates[date_index]} HUMAN CHECK"] = "No" 

    def last_occurrence(): # uses fuzzy matching, still needs to use stripped values
        df_nl.at[row.name, f"{all_website_dates[date_index - 1]} Last Occurrence [Dummy]"] = "Yes"
        for _, rw in df_nl[df_nl[f"{all_website_dates[date_index]} New Item [Dummy]"] == "No"].iterrows(): # go through all unstripped entries in the df and get the description where New Item == "No"
            desc = rw[f"{all_website_dates[date_index]} Description"]  # get the description
            stripped_desc = desc # strip_target_weapon(desc) # also here for higher precision (use strip_target_weapon() in case we need it)
            # perform fuzzy matching
            match_index = -1
            max_similarity = -1
            for idx, description in stripped_df[f"{all_website_dates[date_index - 1]} Description"].items(): 
                similarity = token_sort_ratio(stripped_desc, description)
                if similarity >= 75 and similarity > max_similarity:
                    max_similarity = similarity
                    match_index = idx

            # check if there's a match (avoiding potential IndexError)
            if match_index != -1:
                # update the corresponding "Last Occurrence" with the matched description
                df_nl.at[match_index, f"{all_website_dates[date_index - 1]} Last Occurrence [Dummy]"] = "No"
    
    last_occurrence()

def write_to_df_content_nl(integer, item, max_length):
    global date_index
    global df_content_nl

    # create new column names based on the unique date
    column_1 = f"{all_website_dates[date_index]} Amount"
    column_2 = f"{all_website_dates[date_index]} Description"
    column_3 = f"{all_website_dates[date_index]} Last Occurrence [Dummy]" # gives "Yes"/"No" -> if "Yes", this was the last time this item is used, ie check if a new item got renamed in following entry
    column_4 = f"{all_website_dates[date_index]} New Item [Dummy]" # gives "Yes"/"No"
    column_5 = f"{all_website_dates[date_index]} Change" # change from date A to B
    column_6 = f"{all_website_dates[date_index]} HUMAN CHECK" # marks all changes that are not in [0,1000] or where we match fuzzy (not exact) 
    column_7 = f"{all_website_dates[date_index]}" # visual seperator
    # create a dictionary to hold the new column values
    new_data = {}

    # fill the dictionary with the existing data from the DataFrame
    for col in df_content_nl.columns:
        new_data[col] = df_content_nl[col].tolist() + [""] * (max_length - len(df_content_nl[col]))
    
    # add the new lists to the dictionary
    new_data[column_1] = integer + [""] * (max_length - len(integer))
    new_data[column_2] = item + [""] * (max_length - len(item))
    new_data[column_3] = [""] * max_length
    new_data[column_4] = [""] * max_length
    new_data[column_5] = [""] * max_length
    new_data[column_6] = [""] * max_length
    new_data[column_7] = ["|"] * max_length

    df_content_nl = pd.DataFrame(new_data) # fill df with new entries
    if date_index > 0: # we need at least one entry to compare against 
        df_content_nl.apply(calculate_change, axis=1, df_nl=df_content_nl)
    
    # reset date lists
    matched_indices_change.clear()

    return df_content_nl

def translate_text(text, src='nl', dest='en'):
    # Function to translate text using Google Translate API
    translator = Translator()
    try:
        translation = translator.translate(text, src=src, dest=dest)
        return translation.text
    except Exception as e:
        return text  # Return original text in case of error

def replace_ammo(match):
    # Define a function to replace " en" with "," and "." with ","
    text = match.group(0)
    text = text.replace(" en", ",")
    text = text.replace(".", ",")
    text = text.replace(",", " munitie,")  # Append " munitie" in front of the first comma
    return text

def replace_spare_parts(match):
    # same for spare parts  
    text = match.group(0)
    text = text.replace(" en", ",")
    text = text.replace(".", ",")
    text = text.replace(",", " reservedelen,")  # Append " reservedelen" in front of the first comma
    return text


main()