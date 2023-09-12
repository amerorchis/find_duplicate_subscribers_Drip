import pandas as pd

def save_excel(doubled_emails, output_filename):
    # Sort the list of tuples alphabetically by the first item
    sorted_emails = sorted(doubled_emails, key=lambda x: x[0])

    # Create a DataFrame from the sorted list of tuples
    df = pd.DataFrame(sorted_emails, columns=['Email', 'Equivalent Subscriber'])

    # Save the DataFrame to an Excel file
    df.to_excel(output_filename, index=False)
