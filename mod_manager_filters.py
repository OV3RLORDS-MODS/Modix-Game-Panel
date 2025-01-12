import os
from datetime import datetime
from typing import List, Tuple, Union

# Define the type alias for mod entries
ModEntry = Tuple[str, Union[str, int]]  # (filename, date or size)

def sort_by_name(entries: List[ModEntry]) -> List[ModEntry]:
    """
    Sort the mod entries by filename alphabetically.
    """
    return sorted(entries, key=lambda x: x[0].lower())

def sort_by_date(entries: List[ModEntry]) -> List[ModEntry]:
    """
    Sort the mod entries by modification date in descending order.
    Assumes date is in 'YYYY-MM-DD' format.
    """
    def parse_date(entry):
        try:
            return datetime.strptime(entry[1], '%Y-%m-%d')
        except ValueError:
            return datetime.min
    
    return sorted(entries, key=lambda x: parse_date(x), reverse=True)

def sort_by_size(entries: List[ModEntry]) -> List[ModEntry]:
    """
    Sort the mod entries by file size in descending order.
    """
    return sorted(entries, key=lambda x: x[1], reverse=True)

def sort_by_extension(entries: List[ModEntry]) -> List[ModEntry]:
    """
    Sort the mod entries by file extension alphabetically.
    """
    return sorted(entries, key=lambda x: os.path.splitext(x[0])[1].lower())

def sort_by_creation_date(entries: List[ModEntry]) -> List[ModEntry]:
    """
    Sort the mod entries by file creation date in descending order.
    """
    def get_creation_date(filename):
        try:
            return datetime.fromtimestamp(os.path.getctime(filename))
        except FileNotFoundError:
            return datetime.min
    
    return sorted(entries, key=lambda x: get_creation_date(x[0]), reverse=True)

def sort_combined(entries: List[ModEntry], sort_keys: List[str]) -> List[ModEntry]:
    """
    Sort the mod entries using multiple criteria.
    E.g., ['name', 'date', 'size'] will sort by name first, then date, then size.
    """
    for key in sort_keys:
        if key == 'name':
            entries = sort_by_name(entries)
        elif key == 'date':
            entries = sort_by_date(entries)
        elif key == 'size':
            entries = sort_by_size(entries)
        elif key == 'extension':
            entries = sort_by_extension(entries)
        elif key == 'creation_date':
            entries = sort_by_creation_date(entries)
        else:
            print(f"Unknown sort key: {key}")
            return entries
    return entries

# Example usage:

if __name__ == "__main__":
    # Example data
    mod_entries = [
        ("mod1.zip", 1024),            # filename and size in bytes
        ("mod2.zip", "2024-08-25"),    # filename and modification date
        ("mod3.zip", 2048),
        ("mod4.zip", "2024-08-26"),
    ]

    # Sort by size
    sorted_by_size = sort_by_size(mod_entries)
    print("Sorted by size:", sorted_by_size)

    # Sort by date
    sorted_by_date = sort_by_date(mod_entries)
    print("Sorted by date:", sorted_by_date)

    # Combined sort by name and size
    combined_sort = sort_combined(mod_entries, ['name', 'size'])
    print("Combined sort by name and size:", combined_sort)