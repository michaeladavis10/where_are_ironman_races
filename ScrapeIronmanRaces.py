# Used to add locations on Google Maps here: https://www.google.com/maps/d/u/0/edit?mid=1z3wWmoi6MFwQs9UReqbQUFVVyLWm3znH&usp=sharing
# Also used on RaspPi Server here: https://datastudio.google.com/embed/reporting/85c10805-1156-49dc-bff6-105bb88e3154/page/2ub0C

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

import pandas as pd
import time
import pygsheets

# Open page
url = "https://www.ironman.com/races"
driver = webdriver.Firefox()
driver.get(f"{url}")

# Accept Cookies
cookie_accept = '//*[@id="onetrust-accept-btn-handler"]'
wait = WebDriverWait(
    driver,
    timeout=10,
    poll_frequency=1,
)
element = wait.until(EC.element_to_be_clickable((By.XPATH, cookie_accept))).click()

# Scrape pages
race_list = []

while True:

    # Get info from page
    time.sleep(0.5)
    race_cards = driver.find_elements_by_class_name("race-card")

    for race_card in race_cards:

        # Dates
        race_month = race_card.find_element_by_class_name("race-month").text
        race_day = race_card.find_element_by_class_name("race-day").text
        race_year = race_card.find_element_by_class_name("race-year").text

        # Race Info
        race_name = (
            race_card.find_element_by_class_name("details-left")
            .find_element_by_tag_name("h3")
            .text
        )
        race_location = race_card.find_element_by_class_name("race-location").text
        race_link = race_card.find_element_by_tag_name("a").get_attribute("href")
        race_image = race_card.find_element_by_tag_name("img").get_attribute("src")

        # Course Info
        race_swim = (
            race_card.find_element_by_class_name("swim-type")
            .find_element_by_tag_name("b")
            .text
        )
        race_bike = (
            race_card.find_element_by_class_name("bike-type")
            .find_element_by_tag_name("b")
            .text
        )
        race_run = (
            race_card.find_element_by_class_name("run-type")
            .find_element_by_tag_name("b")
            .text
        )
        race_air_temp = int(
            race_card.find_element_by_class_name("airTemp")
            .find_element_by_tag_name("b")
            .text.split("\xb0")[0]
        )
        race_water_temp = int(
            race_card.find_element_by_class_name("waterTemp")
            .find_element_by_tag_name("b")
            .text.split("\xb0")[0]
        )
        race_airport = (
            race_card.find_element_by_class_name("airport")
            .find_element_by_tag_name("b")
            .text
        )

        # Cleaning up
        ## Race type
        if "70.3" in race_name:
            race_type = "70.3"
        elif "5150" in race_name:
            race_type = "Olympic"
        else:
            race_type = "Full"

        ## Dates
        ### Month
        if race_month == "June":
            race_month = "Jun"
        elif race_month == "July":
            race_month = "Jul"
        elif race_month == "Sept":
            race_month = "Sep"
        elif race_month == "March":
            race_month = "Mar"
        elif race_month == "April":
            race_month = "Apr"
        elif race_month == "TBD":
            race_month = "Dec"
            race_day = "31"
        ### Year/day
        if race_year == "TBD":
            continue
        elif race_year == "":
            continue
        elif race_year == None:
            continue
        elif race_day == "TBD":
            race_day = "01"
        ### Make a complete year
        race_date = pd.to_datetime(race_year + race_month + race_day, format=("%Y%b%d"))

        # Don't mess with names (spaces) due to existing formats
        race_dict = dict()
        race_dict["Race Name"] = race_name
        race_dict["Race Type"] = race_type
        race_dict["Race Date"] = race_date
        race_dict["Location"] = race_location
        race_dict["Swim Type"] = race_swim
        race_dict["Bike Type"] = race_bike
        race_dict["Run Type"] = race_run
        race_dict["Air Temp"] = race_air_temp
        race_dict["Water Temp"] = race_water_temp
        race_dict["Airport"] = race_airport
        race_dict["URL"] = race_link
        race_dict["Race Image"] = race_image

        print(race_name)
        race_list.append(race_dict)

    try:
        next_page_button = driver.find_element_by_css_selector("button.nextPageButton")
        driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
        time.sleep(0.25)
        next_page_button.click()

    except (TimeoutException, WebDriverException) as e:
        print("Last page reached")
        driver.quit()
        break


races_df = pd.DataFrame(race_list)
races_df.to_excel("ironman_races.xlsx", index=False)

# Write to G-Sheets
gc = pygsheets.authorize(service_file="ironmanmap-0773e936d7d8.json")

wb = gc.open("IronmanRaces")
wks = wb.worksheet("title", "Sheet1")
wks.clear()
wks.set_dataframe(races_df, (1, 1))
wks.adjust_column_width(1, len(races_df.columns))
