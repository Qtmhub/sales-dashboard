import pandas as pd
from bs4 import BeautifulSoup
import os

# List of HTML file paths
html_files = [
    "09.04.25.htm",
    "10.04.25.htm",
    "11.04.25.htm",
    "12.04.25.htm",
    "14.04.25.htm",
    "15.04.25.htm"
]

# Function to parse and extract structured data from a single HTML report
def parse_structured_html(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        soup = BeautifulSoup(file, "html.parser")

    rows = soup.find_all("tr")
    parsed_data = []
    current_date = None
    current_time = None
    current_entry = {}

    for row in rows:
        cells = [cell.get_text(strip=True) for cell in row.find_all("td")]

        # Capture date
        for text in cells:
            if "2025" in text:
                current_date = text.strip()
                break

        # Capture time
        for text in cells:
            if "AM" in text or "PM" in text:
                current_time = text.strip()
                break

        # Capture SKU info and unit price
        if len(cells) >= 9 and cells[8] != "":
            current_entry = {
                "Date": current_date,
                "Time": current_time,
                "Receipt": cells[7],
                "StockName": cells[8],
                "UnitPrice": cells[9] if len(cells) > 9 else None
            }

        # Capture qty, amount, and salesperson
        if len(cells) >= 13 and cells[10].isdigit():
            current_entry["Qty"] = int(cells[10])
            current_entry["Amount"] = int(cells[11].replace(",", ""))
            current_entry["SalesPerson"] = cells[12]
            parsed_data.append(current_entry.copy())

    return parsed_data

# Combine all parsed entries into one list
all_data = []
for file in html_files:
    all_data.extend(parse_structured_html(file))

# Convert to DataFrame
sales_df = pd.DataFrame(all_data)

# Preview
print(sales_df.head())
