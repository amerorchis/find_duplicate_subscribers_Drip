import os
import requests
import threading
import time

class DripEmailUtil:
    def __init__(self):
        self.token = os.environ.get('DRIP_TOKEN')
        self.base_url = 'https://api.getdrip.com/v2'
        self.account_id = os.environ.get('DRIP_ACCOUNT')
        self.errors = []

    def get_all_emails(self):

        self.get_first_page()

        # Create a list to hold the thread objects
        threads = []

        # Lock to control access to shared data
        lock = threading.Lock()

        # Create and start a thread for each page
        for i in range(2,self.total_pages + 1):
            thread = threading.Thread(target=self.get_page_emails, args=(lock,i))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        if self.errors:
            raise Exception(f"Failed to fetch {len(self.errors)} page(s): {self.errors}")

        print(f'{len(self.emails)} emails were added to the list out of a total of {self.total_emails}')

    def get_page_emails(self, lock, page_number, retries=3):

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/vnd.api+json'
        }

        url = f'{self.base_url}/{self.account_id}/subscribers?page={page_number}&per_page=1000'

        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                with lock:
                    self.emails.extend([subscriber['email'] for subscriber in data['subscribers']])
                    if page_number % 10 == 0:
                        print(f'Added page {page_number}')
                return

            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    with lock:
                        self.errors.append(page_number)
                    print(f"Failed to fetch page {page_number} after {retries} attempts: {e}")
    
    def get_first_page(self):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/vnd.api+json'
        }
        
        url = f'{self.base_url}/{self.account_id}/subscribers?page=1&per_page=1000'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Assuming the response structure is JSON with email under "email" key
            self.total_pages = data['meta']['total_pages']
            self.total_emails = data['meta']['total_count']
            self.emails = [subscriber['email'] for subscriber in data['subscribers']]
            
            print(f'Added page 1')

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching subscriber emails: {str(e)}")
    
    def write_to_file(self, filename):
        try:
            with open(filename, 'w') as file:
                for email in self.emails:
                    file.write(email + '\n')
            print(f'Emails written to {filename}')
        except Exception as e:
            print(f"Error writing to file: {str(e)}")
    
    def read_emails_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                emails = [line.strip() for line in file]
            self.emails = emails
        except Exception as e:
            print(f"Error reading from file: {str(e)}")

def retrieve_emails():
    drip_list = DripEmailUtil()
    drip_list.get_all_emails()
    # drip_list.read_emails_from_file('files/emails')
    return drip_list.emails
