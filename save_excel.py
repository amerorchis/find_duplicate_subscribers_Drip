"""Write duplicate-subscriber groups to an Excel spreadsheet."""

from openpyxl import Workbook


def save_excel(duplicate_groups, output_filename):
    """Save [(normalized, [variants]), ...] as a two-column spreadsheet."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Normalized Email", "Duplicate Subscribers"])
    for normalized, variants in duplicate_groups:
        sheet.append([normalized, ", ".join(variants)])
    workbook.save(output_filename)
