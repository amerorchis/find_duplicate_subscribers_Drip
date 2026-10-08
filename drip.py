"""Fetch all subscriber emails from the Drip API with bounded concurrency."""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

import requests

MAX_WORKERS = 10
REQUEST_TIMEOUT = 30
PER_PAGE = 1000

logger = logging.getLogger(__name__)


class DripEmailUtil:
    """Client for pulling every subscriber email out of a Drip account."""

    def __init__(self):
        self.token = os.environ.get('DRIP_TOKEN')
        self.account_id = os.environ.get('DRIP_ACCOUNT')
        self.base_url = 'https://api.getdrip.com/v2'
        self.emails = []
        self.total_pages = 0
        self.total_emails = 0
        self.errors = []
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/vnd.api+json',
        })

    def _page_url(self, page_number):
        return (f'{self.base_url}/{self.account_id}/subscribers'
                f'?page={page_number}&per_page={PER_PAGE}')

    def get_all_emails(self):
        """Fetch every page of subscribers, raising if any page fails."""
        self.get_first_page()

        if self.total_pages > 1:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for page_emails in executor.map(self.get_page_emails,
                                                range(2, self.total_pages + 1)):
                    self.emails.extend(page_emails)

        if self.errors:
            raise RuntimeError(f'Failed to fetch {len(self.errors)} page(s): {self.errors}')

        logger.info('%d emails were added to the list out of a total of %d',
                    len(self.emails), self.total_emails)

    def get_page_emails(self, page_number, retries=3):
        """Fetch one page of subscriber emails, retrying with backoff on failure."""
        for attempt in range(retries):
            try:
                response = self.session.get(self._page_url(page_number),
                                            timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                if page_number % 10 == 0:
                    logger.info('Added page %d', page_number)
                return [subscriber['email'] for subscriber in data['subscribers']]

            except requests.exceptions.RequestException:
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.exception('Failed to fetch page %d after %d attempts',
                                     page_number, retries)
                    self.errors.append(page_number)
        return []

    def get_first_page(self):
        """Fetch page 1 and record the total page/email counts from its metadata."""
        try:
            response = self.session.get(self._page_url(1), timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f'Error fetching subscriber emails: {e}') from e

        self.total_pages = data['meta']['total_pages']
        self.total_emails = data['meta']['total_count']
        self.emails = [subscriber['email'] for subscriber in data['subscribers']]

        logger.info('Added page 1')

    def write_to_file(self, filename):
        """Write the fetched emails to a file, one per line (dev helper)."""
        with open(filename, 'w', encoding='utf-8') as file:
            for email in self.emails:
                file.write(email + '\n')
        logger.info('Emails written to %s', filename)

    def read_emails_from_file(self, filename):
        """Load emails from a file instead of the API (dev helper)."""
        with open(filename, 'r', encoding='utf-8') as file:
            self.emails = [line.strip() for line in file if line.strip()]


def retrieve_emails():
    """Fetch and return all subscriber emails from Drip."""
    drip_list = DripEmailUtil()
    drip_list.get_all_emails()
    # drip_list.read_emails_from_file('files/emails')
    return drip_list.emails
