# Module name:  ProjectMerger.py
# Description:  A "simple" python script that allows users to merge together multiple programming block files (.v5blocks or .iqblocks) into one
# Created by:   Caleb Carlson
# Date:         7/4/2023
# Terms of use: Just make sure to give me (Caleb Carlson) credit for this specific file if you use it (this file)


import os
import json
import time
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime


ET.register_namespace('', "http://www.w3.org/1999/xhtml")
platform_detected = False
platform = None

# We frequently need to get the ID of a block
def get_block_id(element: ET.Element) -> str:
    return dict(element.attrib)['id']


# Function to get project files from folder
def get_project_files(local_directory: str, console_output: bool = True) -> list[str]:

    global platform, platform_detected

    file_paths = []

    if console_output:
        print("\nFinding project files... \n")

    # Search the given folder for any .v5blocks or .iqblocks files (will also search in subfolders; organizing a project with folders is okay)
    for root, dirs, files in os.walk(local_directory):
            for file in files:
                extension = os.path.splitext(file)[-1]
                if extension == ".v5blocks" or extension == ".iqblocks":
                    if not platform_detected:
                        platform_detected = True
                        platform = extension
                    if extension == platform:
                        file_paths.append(os.path.join(root, file))
                        if console_output:
                            print("Found file at path:              {}".format(file_paths[-1]))

    
    if console_output:
        print("")

    return file_paths


# Function to get appropriate xml data from a .v5blocks or .iqblocks file
def get_xml_data_from_file(local_file_path: str) ->str:
    
    print("Retrieving XML-str data from:    {}".format(local_file_path))

    # Load JSON data from file
    with open(local_file_path) as file:
        json_content = json.loads(file.readline())

    # Retrieve and then return a string representing the XML data contained within the JSON under the key "workspace"
    return json_content['workspace']

# Function to replace appropriate xml data from a .v5blocks or .iqblocks file
def replace_xml_data_in_file(local_file_path: str, content_to_replace_with: str) -> dict:
    
    
    print("\nReplacing XML-block data in:     {}\n".format(local_file_path))

    # Load JSON data from file
    with open(local_file_path) as file:
        json_content = json.loads(file.readline())

    json_content['workspace'] = content_to_replace_with

    return json_content


# Function to get appropriate element xml data from a .v5blocks or .iqblocks file
def get_xml_element_data_from_file(local_file_path: str) ->ET.Element:

    print("Retrieving ET.Element data from: {}".format(local_file_path))

    # Load JSON data from file
    with open(local_file_path) as file:
        json_content = json.loads(file.readline())

    # Retrieve and then return an ET.Element object representing the XML data contained within the JSON under the key "workspace"
    return ET.ElementTree(ET.fromstring(json_content['workspace']))


# Function to get any <{http://www.w3.org/1999/xhtml}block> elements within a given XML structure (a string)
def get_block_elements_from_xml(raw_xml_data: str, local_file_path: str) -> list[ET.Element]:

    # Create an ElementTree from raw XML text
    tree = ET.ElementTree(ET.fromstring(raw_xml_data))

    # Get the root element
    root = tree.getroot()

    # Find all 'block' elements that are direct children of the 'xml' element and return them
    blocks = root.findall('./{http://www.w3.org/1999/xhtml}block')

    # Report the amount of block elements found
    length_of_blocks_string = len(str(len(blocks)))
    length_of_blocks_string += 1 if len(blocks) != 1 else 0
    print("found {} block element{} from:{}{}".format(
        len(blocks),
        's' if len(blocks) != 1 else '',
        ' ' * (7 - length_of_blocks_string),
        local_file_path
    ))
    
    return blocks


# Function that will search each project for any XML block elements and compile a list of them
def get_block_elements_from_projects(project_folder_path: str) -> list[ET.Element]:

    print("\n###########################################\n# Retrieving blocks from project files    #\n###########################################")

    # Retrieve list of .v5blocks or .iqblocks files within project folder
    project_files = get_project_files(project_folder_path)

    # Retrieve the workspace XML data stored in each project file
    raw_xml_project_data = []
    for project_file in project_files:
        raw_xml_project_data.append((get_xml_data_from_file(project_file), project_file))

    print("")

    # Iterate through the retrieved raw XML data and extract any <{http://www.w3.org/1999/xhtml}block> elements
    xml_block_elements = []
    for raw_xml in raw_xml_project_data:
        current_project_xml_block_elements = get_block_elements_from_xml(raw_xml[0], raw_xml[1])
        for xml_block_element in current_project_xml_block_elements:
            xml_block_elements.append(xml_block_element)
    
    print("")

    return xml_block_elements


# Find an element in a list with a specific ID:
def get_element_with_id(element_list: list[ET.Element], id: str) -> ET.Element:

    # Search the list for the correct element and return it
    for element in element_list:
        if get_block_id(element) == id:
            return element

    return None

# Appends block elements to the target merge file
def append_xml_block_elements_to_merge_project(merge_project_file_path: str, blocks_to_append: list[ET.Element]) -> ET.Element:

    print("###########################################\n# Appending retrieved blocks to main file #\n###########################################\n")

    # Retrieve the XML Tree structure from the destination project file
    tree = get_xml_element_data_from_file(merge_project_file_path)
    root = tree.getroot()

    print("")

    # Load in existing block elements
    previously_existing_blocks = root.findall('./{http://www.w3.org/1999/xhtml}block')

    # Compile a list of block ID's from existing blocks
    previously_existing_block_ids = []
    for block in previously_existing_blocks:
        previously_existing_block_ids.append(get_block_id(block))

    # Remove previously existing blocks that must be removed (blocks previously brought in from projet files)
    elements_to_be_removed = []
    for element in blocks_to_append:
        id = get_block_id(element)
        if id in previously_existing_block_ids:
            elements_to_be_removed.append(get_element_with_id(previously_existing_blocks, id))

    for element_to_be_removed in elements_to_be_removed:
        try:
            root.remove(element_to_be_removed)
            print("Removing outdated block:         id=\"{}\"".format(get_block_id(element_to_be_removed)))
        except ValueError:
            pass

    print("")

    # A list that will hold previously appended block IDs
    ids_of_appended_blocks = []

    # A list for console output
    warnings = []

    # Add block elements to root
    for block in blocks_to_append:
        if not get_block_id(block) in ids_of_appended_blocks:
            root.append(block)
            ids_of_appended_blocks.append(get_block_id(block))
            print("Inserting block:                 id=\"{}\"".format(get_block_id(block)))
        else:
            warnings.append("[WARNING] Omitted adding a duplicate block! Block id: \"{}\"".format(get_block_id(block)))

    # Display any warnings
    if warnings:
        print("")
    for warning in warnings:
        print(warning)

    return root


def escape_quotes_in_attributes(xml_string):
    escaped_string = xml_string.replace('"', r'\"')
    return escaped_string

def merge_files(modules_folder: str, path_to_merge_file: str):

    # Get the list of XML block elements from the projects in the "Modules" folder
    elements = get_block_elements_from_projects(modules_folder)

    # Append the XML block elements to the target merge project file (path_to_merge_file)
    root = append_xml_block_elements_to_merge_project(path_to_merge_file, elements)

    # Convert the updated XML structure to a string representation
    xml_string = ET.tostring(root, encoding='unicode', method='xml')

    # Store the modified XML string in the 'modified_xml_string' variable
    modified_xml_string = xml_string

    # Load the existing JSON data from the target merge project file
    json_file = replace_xml_data_in_file(path_to_merge_file, modified_xml_string)

    # Open the target merge project file in write mode
    merge_file = open(path_to_merge_file, 'w')

    # Write the updated JSON data back to the merge project file
    merge_file.write(json.dumps(json_file))

    # Flush the file to ensure the data is written immediately
    merge_file.flush()


def create_previous_version(path_to_merge_file: str, maximum_previous_versions: int):

    print("###########################################\n# Creating backup file                    #\n###########################################\n")

    maximum_previous_versions -= 1

    # Extract the directory and filename from the provided file path
    folder_directory, file_name = os.path.split(path_to_merge_file)

    # Create "PreviousVersions" folder if it doesn't exist
    previous_versions_dir = os.path.join(folder_directory, "PreviousVersions")
    if not os.path.exists(previous_versions_dir):
        os.makedirs(previous_versions_dir)
        print("Created PreviousVersions folder.\n")

    # Get the list of files in the "PreviousVersions" folder
    previous_versions_files = os.listdir(previous_versions_dir)

    # Check if the number of previous versions exceeds the limit (maximum_previous_versions)
    if len(previous_versions_files) >= maximum_previous_versions:
        # Sort previous versions files by modification time (oldest to newest)
        previous_versions_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(previous_versions_dir, x))
        )

        # Remove the oldest files until the count is within the limit
        files_to_remove = previous_versions_files[: len(previous_versions_files) - maximum_previous_versions]
        for file_to_remove in files_to_remove:
            os.remove(os.path.join(previous_versions_dir, file_to_remove))
            print("Removed old backup:              {}".format(os.path.join(previous_versions_dir, file_to_remove)))

    print("")

    # Get the current date and time
    now = datetime.now()
    date_suffix = now.strftime("%Y%m%d_%H%M%S")

    # Generate the new file name with the date suffix
    new_file_name = f"{file_name.split('.')[0]}_{date_suffix}.{file_name.split('.')[1]}"

    # Create a copy of the file with the new name in the "PreviousVersions" folder
    shutil.copy2(path_to_merge_file, os.path.join(previous_versions_dir, new_file_name))

    print("Created new backup:              {}".format(os.path.join(previous_versions_dir, new_file_name)))


if __name__ == "__main__":

    modules_folder = "Modules"
    merge_folder = "Merge"

    path_to_merge_file = get_project_files(merge_folder, console_output=False)[0]
    maximum_previous_versions = 5

    # Allow the console to open to allow messages to be printed
    time.sleep(0.25)

    create_previous_version(path_to_merge_file, maximum_previous_versions)
    merge_files(modules_folder, path_to_merge_file)

    print("Complete!")
    input()
    