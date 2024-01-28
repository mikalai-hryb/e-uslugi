import concurrent.futures
import requests
import sys

from datetime import date, timedelta

# https://www.e-uslugi.mazowieckie.pl/delegate/services/guest/subjects/176/timeframes/2024-01-30/next/date
URL_TEMPLATE = 'https://www.e-uslugi.mazowieckie.pl/delegate/services/guest/subjects/176/timeframes/{date}/next/date'
URL_TO_OPEN = 'https://www.e-uslugi.mazowieckie.pl/umow-wizyte#/visit-selection'
DAYS_TO_CHECK = 30
DATE_POSITION = slice(84, 94)
RESULTS = []


def generate_urls(number_of_days=2):
    lst = []
    today = date.today()
    for i in range(number_of_days):
        day = today + timedelta(i)
        lst.append(URL_TEMPLATE.format(date=day))
    return lst


def fetch_url(url):
    try:
        response = requests.get(url)
        # Process the response or do anything with it here
        print(f"URL: {url}, Status Code: {response.status_code}")
        RESULTS.append({
            "url": url,
            "status_code": response.status_code,
            "message": response.json()['message'],
            "date": url[DATE_POSITION]

        })
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")


def send_message(chat_id, bot_token, message="hello"):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?parse_mode=HTML&chat_id={chat_id}&text={message}"
    print(url)
    print(requests.get(url).json()) # this sends the message


if __name__ == "__main__":
    chat_id = str(sys.argv[1])
    bot_token = str(sys.argv[2])

    # Use ThreadPoolExecutor for parallel execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for each URL
        urls = generate_urls(DAYS_TO_CHECK)
        futures = [executor.submit(fetch_url, url) for url in urls]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

    have_date = False
    messages = ['<b>Ёсць рэзервацыя на:</b>']
    for result in sorted(RESULTS, key=lambda d: d['date']):
        if result['message'] != 'Brak wizyt w najbliższym czasie':
            messages.append(f'* {result["date"]}')
            have_date = True
    if have_date:
        messages.append(URL_TO_OPEN)

    if len(messages) > 1:
        print('sending a message')
        send_message(chat_id, bot_token, '\n'.join(messages))
