import argparse
import os
import json
import re
from slugify import slugify  # You'll need to install this library using `pip install python-slugify`

def read_config_file(config_filename):
    with open(config_filename, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def read_markdown_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def extract_clean_title(title):
    clean_title = re.sub(r'\s*\([^)]*\)|\{[^}]*\}}', '', title).strip()
    return clean_title

def dict_key_associated_with_value(mapping, value):
    return next((key for key, val in mapping.items() if val == value), None)

def get_value_with_default(dictionary, key, default='UNKNOWN'):
    return dictionary.get(key, default)

def get_value_using_mapped_key(row, column_mapping, desired_value, default='UNKNOWN'):
    mapped_key = dict_key_associated_with_value(column_mapping, desired_value)
    return get_value_with_default(row, mapped_key, default)


def create_hugo_content(table_data, output_dir, column_mapping):
    os.makedirs(output_dir, exist_ok=True)

    for row in table_data:

        title_column = next((col for col in column_mapping if "title" in column_mapping[col].lower()), None)
        title = row[title_column] if title_column in row else 'Untitled'
        clean_title = extract_clean_title(title)
        title_kebab = slugify(clean_title)

        thumbnail_file = re.search(r'src="([^"]+)"', title).group(1) if re.search(r'src="([^"]+)"', title) else None
        index_column = next((col for col in column_mapping if "index" in column_mapping[col].lower()), None)
        index = row.get(index_column, 'No Index')  # Default to 'No Index' if index is missing

        finished_date = get_value_using_mapped_key(row, column_mapping, 'finished_date', 'UNKNOWN')
        release_year = get_value_using_mapped_key(row, column_mapping, 'release_year', 'UNKNOWN')
        rating = get_value_using_mapped_key(row, column_mapping, 'rating', 'No rating available')
        description = get_value_using_mapped_key(row, column_mapping, 'description', 'No description available')

        content = f"+++\ndate: {finished_date}\n"
        print(clean_title)
        content += f"title: \"(Book #{index}) {clean_title}\"\n"  # Format the title as "(INDEX) TITLE"
        content += f"frontpage: \"true\"\n"
        content += f"cover: {thumbnail_file}\n"
        content += f"tags: ['books']\n"
        content += f"+++\n\n"

        content += f"Release year: {release_year}\n\n"
        content += f"{rating}\n\n"
        content += f"Read [the notes I wrote]({description}) from this book.\n"

        filename = f"{title_kebab}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown table to Hugo content files")
    parser.add_argument("filename", help="Input Markdown file containing the table")
    parser.add_argument("--config", default="column_mapping.json", help="JSON configuration file for column mapping (default: column_mapping.json)")
    args = parser.parse_args()

    output_directory = 'hugo_content'  # Replace with your desired output directory

    markdown_content = read_markdown_file(args.filename)
    rows = markdown_content.strip().split('\n')
    column_names = rows[0].strip().split('|')

    table_data = []
    for row in rows[1:]:
        row_values = row.strip().split('|')
        row_data = {col_name.strip(): value.strip() for col_name, value in zip(column_names, row_values)}
        #print(row_data) #1
        table_data.append(row_data)

    config = read_config_file(args.config)
    column_mapping = config.get("column_mapping", {})

    create_hugo_content(table_data, output_directory, column_mapping)

if __name__ == "__main__":
    main()

