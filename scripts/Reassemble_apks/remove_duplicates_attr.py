import xml.etree.ElementTree as ET
from lxml import etree
import sys
import os
import glob
import subprocess

def remove_duplicate_attributes(file_path):
    try:
        # Parse the XML file
        parser = etree.XMLParser(recover=True)
        tree = ET.parse(file_path, parser)
        root = tree.getroot()

        # Traverse through all elements in the XML tree
        for elem in root.iter():
            # Check for duplicate attributes by storing them in a dictionary
            seen_attributes = {}
            attrib_to_remove = []

            for key, value in elem.attrib.items():
                if key in seen_attributes:
                    attrib_to_remove.append(key)
                else:
                    seen_attributes[key] = value

            # Remove duplicate attributes from the element
            for key in attrib_to_remove:
                del elem.attrib[key]

        # Save the modified XML file
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print(f"Processed and removed duplicates in: {file_path}")

    except ET.ParseError as e:
        print(f"Error parsing XML file {file_path}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to process all XML files in a directory
def process_directory(directory_path):
    for root_dir, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith(".xml"):
                file_path = os.path.join(root_dir, file_name)
                remove_duplicate_attributes(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_duplicates.py <path_to_directory_or_file>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        process_directory(input_path)
    elif os.path.isfile(input_path) and input_path.endswith(".xml"):
        remove_duplicate_attributes(input_path)
    else:
        print("Please provide a valid XML file or directory containing XML files.")
