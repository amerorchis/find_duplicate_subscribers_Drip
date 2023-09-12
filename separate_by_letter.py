from collections import defaultdict

def separate_by_letter(email_list):
    # Create a dictionary to hold email lists grouped by the first letter
    email_lists_by_first_letter = defaultdict(list)

    # Distribute email addresses into their respective lists
    for email in email_list:
        first_letter = email[0].lower()  # Get the first letter and convert to lowercase
        email_lists_by_first_letter[first_letter].append(email)

    return email_lists_by_first_letter
