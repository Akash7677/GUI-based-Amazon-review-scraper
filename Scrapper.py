import configparser
import json
import os
import re
import time
import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from selectolax.parser import HTMLParser
import pandas as pd

SBR_WS_CDP = 'wss://brd-customer-hl_be765d4f-zone-scraping_browser1:hyoour9civ1c@brd.superproxy.io:9222'

proxy_flag = False

review_body_css = '[data-hook="review-body"]'
review_title_css = 'a[data-hook="review-title"]'
review_ratings_css = 'i[data-hook="review-star-rating"] span'
sign_in_page_locator = '#ap_email'
logo = '#nav-logo-sprites'
pg_in = 10
retry_url = []
test_url = 'https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0'
test_flag = False
def get_html(page, page_no, url_, max_retries=3, initial_delay=2):
    global proxy_flag
    retries = 0
    delay = initial_delay

    # Checks the retry count and runs until retries are over
    while retries <= max_retries:
        try:
            # Check if retry_url array is not empty
            if retry_url:
                # Carry on withretry url
                new_url = retry_url[0]
            else:
                matchCase = 'pageNumber={}'
                # format page number for next iteration, after retry_url is processed
                if not matchCase in url_:
                    modified_url = re.sub(r'pageNumber=\d*', r'pageNumber={}', url_)

                    new_url = modified_url.format(str(page_no))
                    # print(new_url)
                else:
                    # Continue with normal operation
                    new_url = url_.format(str(page_no))
                    # print(new_url)
            page.goto(new_url)
            # check if got blocked and sign in page is shown
            # if not page.is_visible(logo):
            if not page.is_visible(logo):
                print("Sign-in page detected. Starting the Proxy.")
                # ----------------------- Testing retry mechenism-------------------------------
                if not test_flag:
                    retry_url.append(
                        'https://www.amazon.in/product-reviews/B0B9BL9T4H/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=positive&reviewerType=all_reviews&pageNumber=3#reviews-filter-bar')
                    print("URL appended forcefully")
                    # print(f"URL : {retry_url[0]}")
                else:
                    retry_url.append(new_url)

                # ----------------------- Testing retry mechenism -------------------------------
                # append the url for the retry
                retry_url.append(new_url)
                print(f"url: {retry_url[0]}")
                # initiate proxy connection
                proxy_flag = True
                # stop execution of current instance
                return None
            # pasre html content
            html = HTMLParser(page.content())
            # Clear the retry_url list if any url is there
            retry_url.clear()
            # return the page source
            return html
        except Exception as e:
            # Through exception and retry
            print(f"Error in get_html: {e}")
            retries += 1
            if retries <= max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("Max retries reached. Giving up.")
                return None

def map_product(product_mapping):
    # Map product and link from the config file
    product_mapping_dict = {}
    for key, value in product_mapping.items():
        product_mapping_dict[key.strip()] = value.strip()
    transformed_dict = {key: value.split(',') for key, value in product_mapping_dict.items()}
    return transformed_dict

def format_url(url_):
    # extract asin from the url
    asin_match = re.search(r'/dp/([A-Z0-9]{10})/', url_)
    asin = asin_match.group(1)
    # format the url for paginatioon
    url = f'https://www.amazon.in/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=positive&reviewerType=all_reviews&pageNumber=1#reviews-filter-bar'
    url = url.replace('pageNumber=1', 'pageNumber={}')
    return url, asin

def strip_json(review_text):
    text = f"""
        {review_text}
    """
    text = text.split("                                                ")
    fin_text = text[-1].strip()
    return fin_text

def parse_html(html):
    # Initiate empty dictionary to store the data
    reviews = []
    # Find the respective data
    review_title = html.css(review_title_css)
    review_body = html.css(review_body_css)
    review_star = html.css(review_ratings_css)
    # Check if data contains all three fiels
    if review_body and len(review_body) == len(review_title) == len(review_star):
        for index in range(len(review_body)):
            rev_title = review_title[index].text().replace("\n", "").strip().split(" ")
            rev_title = " ".join(rev_title[5:]).lstrip(" ")
            rev_body = review_body[index].text().replace("\n", "").strip()
            rev_star = review_star[index].text().replace("\n", "").strip()

            # Check if the review body has at least 5 words
            if len(rev_body.split()) >= 5 and (not("{" in rev_body)):
                data = {
                    "rating": rev_star,
                    "title": rev_title,
                    "body": rev_body
                }
                reviews.append(data)
            else:
                if "}" in rev_body:
                    rev_body_ext = strip_json(rev_body)
                    data = {
                        "rating": rev_star,
                        "title": rev_title,
                        "body": rev_body_ext
                    }
                    reviews.append(data)
                else:
                    print(f"Discarding review: {rev_body}")
            # return data as dataframe
        df = pd.DataFrame(reviews)
        return df, len(df)
    else:
        # return empty dataframe
        print("No reviews found.")
        return pd.DataFrame(), len(pd.DataFrame())

def export_to_excel(excel_filename, df):
    if os.path.exists(excel_filename):
        # Append to existing Excel file
        existing_df = pd.read_excel(excel_filename, engine='openpyxl')
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(excel_filename, index=False, engine='openpyxl')
        # print(f'Data saved to {excel_filename}')
    else:
        # Create a new Excel file
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        # print(f'Excel file created at {os.path.abspath(excel_filename)}')

total_scrapped = 0
def extract_per_page(page, asin, url, product, output_folder):
    global total_scrapped, test_flag
    file_name = f'Amz_{asin}_{product}.xlsx'
    file_path = os.path.join(output_folder, file_name)

    # find the page number in url
    match_group = re.search(r'pageNumber=(\d+)', url)
    # print(f'match group: {match_group}')
    if match_group is not None:
        # if page number found then, start execution from where it got stopped
        start_page = int(match_group.group(1))
    else:
        # continue normal operation
        start_page = 1
    # iterate over pages for the review scrapping
    for pg in range(start_page, pg_in+1):
        # ----------------- Testing retry mechenism ---------------
        if pg == 3 and test_flag:
            print("Test started")
            url = test_url
            test_flag = False
        # # ----------------- Testing retry mechenism ---------------
        html = get_html(page, page_no=pg, url_=url)
        # stop execution is html page source is None
        if html is None:
            return
        time.sleep(0.5)
        revs, reviews_count = parse_html(html)
        if not revs.empty:  # Check if the DataFrame is not empty
            total_scrapped += reviews_count
            export_to_excel(excel_filename= file_path, df=revs)
            print(f"page {pg} scrapped....")
        else:
            print("All reviews extracted")
            break


def run(product, url, asin, output_folder):
    # start playwright instance
    pw = sync_playwright().start()
    # check if needs to run in proxy or normal
    if proxy_flag:
        # check if needs to start from where execution is stopped
        if retry_url:
            try:
                browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
                print("Proxy started")
                page = browser.new_page()
                stealth_sync(page)
                extract_per_page(page, asin, url=url, product=product, output_folder=output_folder)
                browser.close()
                pw.stop()
            except Exception as e:
                print(f"Exception happened: {e}")
                print("Please check, if credits are available proxy")

        # Start normal operation in proxy mode
        else:
            try:
                browser = pw.chromium.connect_over_cdp(SBR_WS_CDP)
                page = browser.new_page()
                stealth_sync(page)
                extract_per_page(page, asin, url=url, product=product, output_folder=output_folder)
                browser.close()
                pw.stop()

            except Exception as e:
                print(f"Exception happened: {e}")
                print("Please check, if credits are available for the proxy")

    # else keep running in Normal mode
    else:
        browser = pw.chromium.launch(headless=True)
        # browser = pw.chromium.launch()
        page = browser.new_page()
        stealth_sync(page)
        extract_per_page(page, asin, url=url, product=product, output_folder=output_folder)
        browser.close()
        pw.stop()

    print(f"Total review: {total_scrapped}")

def parse_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config_data = json.load(file)

        if "urls" in config_data:
            product_mapping = config_data["urls"]
            # Map the product and URL
            url_map = map_product(product_mapping)
            return url_map
        else:
            print("Error: 'urls' key not found in the configuration.")
            return None
    except json.JSONDecodeError as e:
        # Handle JSON decoding error
        print(f"Error decoding JSON in config file: {e}")
        return None
    except Exception as e:
        # Handle other types of errors
        print(f"An unexpected error occurred: {e}")
        return None

def check_url(url_map):
    for prod, link in url_map.items():
        try:
            url, asin = format_url(str(link))
            if url and asin:
                return True
        except:
            print("Please check URL(s) you provided. There might be some mistake")
            return False

def main(prod_map, output_folder=str(os.getcwd())):
    global total_scrapped
    url_map = prod_map
    current_date = datetime.datetime.now().date()

    # Check if the current date is 2024
    if current_date.year == 2024:
        print("Error: Compatibility issue with Playwright module. Please update the package.")
        return False
    # print(url_map)
    # Iterate over the number of products, to which data needs to be extracted
    checked = check_url(url_map)
    if not checked:
        return False
    for prod, link in url_map.items():
        url, asin = format_url(str(link))
        if "[" and "'" in url:
            url = url.strip("[").strip("]").strip("'")
        run(product=prod, url=url, asin = asin, output_folder=output_folder)
        # if retry URL is found the run with retry URL
        if retry_url:
            run(product=prod, url=retry_url[0], asin = asin, output_folder=output_folder)
        total_scrapped = 0
    return True

if __name__ == "__main__":
    url_map = parse_config('config.json')
    main(url_map)