"""Write duplicate-subscriber groups to an Excel spreadsheet."""

import pandas as pd


def save_excel(duplicate_groups, output_filename):
    """Save [(normalized, [variants]), ...] as a two-column spreadsheet."""
    rows = [(normalized, ', '.join(variants)) for normalized, variants in duplicate_groups]
    df = pd.DataFrame(rows, columns=['Normalized Email', 'Duplicate Subscribers'])
    df.to_excel(output_filename, index=False)
