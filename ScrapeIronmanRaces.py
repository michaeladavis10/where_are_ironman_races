# Used to add locations on Google Maps here: https://www.google.com/maps/d/u/0/edit?mid=1z3wWmoi6MFwQs9UReqbQUFVVyLWm3znH&usp=sharing

from selenium import webdriver
import pandas as pd
import time
import pygsheets

url = "https://www.ironman.com/races"

driver = webdriver.Firefox()

driver.get(f"{url}")

cookie_accep = '//*[@id="onetrust-accept-btn-handler"]'

driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()

races_df = pd.DataFrame()
race_list = []

for page in range(14):
    for race in range(1, 16):
        try:

            race_dict = {}

            # Safety
            for variable in [
                "race_name",
                "race_type",
                "race_location",
                "race_link",
                "race_swim",
                "race_bike",
                "race_run",
                "race_air_temp",
                "race_water_temp",
                "race_airport",
                "race_image",
                "race_month",
                "race_day",
                "race_year",
                "race_date",
            ]:
                try:
                    del variable
                except:
                    pass

            race_name = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[1]/div[1]/h3"
            ).text
            if "70.3" in race_name:
                race_type = "70.3"
            elif "5150" in race_name:
                race_type = "Olympic"
            else:
                race_type = "Full"

            race_dict["Race Name"] = race_name
            race_dict["Race Type"] = race_type

            race_month = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[1]/div[1]/p[1]"
            ).text
            race_day = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[1]/div[1]/p[2]"
            ).text
            race_year = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[1]/div[1]/p[3]"
            ).text

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

            if race_year == "TBD":
                continue
            elif race_year == "":
                continue
            elif race_year == None:
                continue
            elif race_day == "TBD":
                race_day = "01"

            race_date = pd.to_datetime(
                race_year + race_month + race_day, format=("%Y%b%d")
            )
            race_dict["Race Date"] = race_date

            race_location = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[1]/div[1]/p[3]"
            ).text
            race_dict["Location"] = race_location

            race_swim = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[1]/p/b"
            ).text
            race_dict["Swim Type"] = race_swim
            race_bike = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[2]/p/b"
            ).text
            race_dict["Bike Type"] = race_bike
            race_run = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[3]/p/b"
            ).text
            race_dict["Run Type"] = race_run
            race_air_temp = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[4]/p/b"
            ).text
            race_dict["Air Temp"] = race_air_temp
            race_water_temp = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[5]/p/b"
            ).text
            race_dict["Water Temp"] = race_water_temp
            race_airport = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[2]/div[6]/p/b"
            ).text
            race_dict["Airport"] = race_airport

            race_link = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[2]/div[1]/div[2]/a"
            ).get_attribute("href")
            race_dict["URL"] = race_link

            race_image = driver.find_element_by_xpath(
                f"/html/body/div[6]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[{race}]/div[1]/img"
            ).get_attribute("src")
            race_dict["Race Image"] = race_image

            race_list.append(race_dict)

        except Exception as e:
            print(race_name)
            print(race_year)
            print(race_month)
            print(race_day)
            print(e)
            continue

    try:
        next_page_button = driver.find_element_by_css_selector("button.nextPageButton")
        driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
        time.sleep(0.25)
        next_page_button.click()

    except Exception as e:
        print(e)
        pass

    time.sleep(0.5)


driver.quit()

races_df = pd.DataFrame(race_list)
races_df

races_df.to_excel("ironman_races.xlsx", index=False)

# Write to G-Sheets
gc = pygsheets.authorize(service_file="ironmanmaps-cce634a56b5e.json")

wb = gc.open("140.6")
wks = wb.worksheet("title", "Sheet1")
wks.clear()
wks.set_dataframe(races_df[races_df["Race Type"] == "Full"], (1, 1))
wks.adjust_column_width(1, len(races_df.columns))

wb = gc.open("70.3")
wks = wb.worksheet("title", "Sheet1")
wks.clear()
wks.set_dataframe(races_df[races_df["Race Type"] == "70.3"], (1, 1))
wks.adjust_column_width(1, len(races_df.columns))

wb = gc.open("Olympic")
wks = wb.worksheet("title", "Sheet1")
wks.clear()
wks.set_dataframe(races_df[races_df["Race Type"] == "Olympic"], (1, 1))
wks.adjust_column_width(1, len(races_df.columns))
