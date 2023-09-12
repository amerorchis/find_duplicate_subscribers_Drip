import re

def are_emails_equivalent(email1, email2):
    # Define the regex pattern to extract username and domain from an email address
    email_pattern = r'^([^@]+)@([^@]+)$'

    # Extract username and domain from the first email
    match1 = re.match(email_pattern, email1)
    if not match1:
        raise ValueError("Invalid email format for email1")
    username1, domain1 = match1.groups()

    # Extract username and domain from the second email
    match2 = re.match(email_pattern, email2)
    if not match2:
        raise ValueError("Invalid email format for email2")
    username2, domain2 = match2.groups()

    # Remove dots and anything after '+' from the usernames
    if domain1 not in ['outlook.com', 'hotmail.com', 'yahoo.com']:
        username1 = re.sub(r'\.', '', username1)
    
    if domain2 not in ['outlook.com', 'hotmail.com', 'yahoo.com']:
        username2 = re.sub(r'\.', '', username2)

    username1 = re.sub(r'\+.*', '', username1)
    username2 = re.sub(r'\+.*', '', username2)

    email_simple1 = username1 + '@' + domain1
    email_simple2 = username2 + '@' + domain2

    return email_simple1 == email_simple2

# Function to check equivalence within a list
def check_equivalence(emails):
    letter = emails[0][0].upper()
    doubled_emails = []

    print(f'Starting letter {letter}')
    for i in range(len(emails)):
        for j in range(i+1, len(emails)):
            if are_emails_equivalent(emails[i], emails[j]):
                doubled_emails.append((emails[i], emails[j]))
                # print((emails[i], emails[j]))
    
    print(f'Finished letter {letter}')
    return doubled_emails
