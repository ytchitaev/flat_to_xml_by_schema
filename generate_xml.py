import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import json
import jsonschema
from typing import Any, Dict, Optional

# read / write file function

def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Reads JSON data from a file and returns it as a Python object."""
    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
        return json_data
    except FileNotFoundError:
        return None


def write_file(filename: str, content: str, encoding: str = "iso-8859-1") -> None:
    """Writes the content to a file."""
    with open(filename, "w", encoding=encoding) as file:
        file.write(content)


# build xml from json mapping functions

def lowercase_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """Lowercase all dictionary keys."""
    return {k.lower(): v for k, v in data.items()}

def process_element_key_or_value(element: str, data: Dict[str, Any]) -> Optional[str]:
    """Process the key or value of an element, performing substitutions if necessary."""
    data = lowercase_dict_keys(data)
    # apply substitutions
    if element.startswith("@"):
        key = element[1:].lower()
        value = data.get(key, "")
        # flag for attribute removal
        return value if value != "#NULL#" else None
    else:
        return element


def process_element_attributes(
    element_attributes: Dict[str, str], data: Dict[str, Any]
) -> Dict[str, Optional[str]]:
    """Process the attributes of an element, performing substitutions if necessary."""
    data = lowercase_dict_keys(data)
    attributes = {}
    for key, value in element_attributes.items():
        # apply substitutions
        if value.startswith("@"):
            attr_key = value[1:].lower()
            attr_value = data.get(attr_key, "")
            # flag for element removal
            attributes[key] = attr_value if attr_value != "#NULL#" else None
        else:
            attributes[key] = value
    return attributes


def build_xml(element_def: Dict[str, Any], data: Dict[str, Any]) -> ET.Element:
    """Builds an XML element based on the element definition and dataset."""
    root_element = ET.Element(element_def["_name"])
    build_xml_recursive(root_element, element_def, data)
    return root_element


def build_xml_recursive(
    parent_element: ET.Element, element_def: Dict[str, Any], data: Dict[str, Any]
) -> None:
    """Builds the XML element recursively based on the element definition and dataset."""
    # if the target element is a header, build structure once only
    if element_def["_type"] == "header":
        build_xml_recursive_header(parent_element, element_def, data)
    # if the target element is a header, build structure iteratively for each dataset row
    elif element_def["_type"] == "row":
        for item in data:
            build_xml_recursive_row(parent_element, element_def, item)


def build_xml_recursive_header(
    parent_element: ET.Element, element_def: Dict[str, Any], data: Dict[str, Any]
) -> None:
    """Builds the header XML element recursively based on the element definition and dataset."""
    # populate header attributes from xml definition
    if "_attributes" in element_def:
        parent_element.attrib.update(element_def["_attributes"])
    # populate header value from xml definition
    if "_value" in element_def:
        parent_element.text = element_def["_value"]
    # recurse to children elements from a header element
    if "_children" in element_def:
        for child_def in element_def["_children"]:
            if child_def["_type"] == "header":
                child_element = ET.SubElement(parent_element, child_def["_name"])
                build_xml_recursive(child_element, child_def, data)
            if child_def["_type"] == "row":
                build_xml_recursive(parent_element, child_def, data)


def build_xml_recursive_row(
    parent_element: ET.Element, element_def: Dict[str, Any], data: Dict[str, Any]
) -> None:
    """Builds the row XML element recursively based on the element definition and dataset."""
    row_element = ET.SubElement(parent_element, element_def["_name"])
    # populate row attributes from xml definition, apply substitutions or removing if #NULL#
    if "_attributes" in element_def:
        attributes = process_element_attributes(element_def["_attributes"], data)
        if attributes is None:
            attributes = {}
        row_element.attrib.update(attributes)
    # populate row value from xml definition, apply substitutions or removing if #NULL#
    if "_value" in element_def:
        value = process_element_key_or_value(element_def["_value"], data)
        if value is not None:
            row_element.text = value
        else:
            parent_element.remove(row_element)
    # recurse to children elements from a row element
    if "_children" in element_def:
        for child_def in element_def["_children"]:
            build_xml_recursive_row(row_element, child_def, data)


# output xml functions

def get_xml_string(element: ET.Element, encoding: str = "iso-8859-1") -> str:
    """Returns the XML string representation of the element."""
    return ET.tostring(element, encoding=encoding).decode()


def get_pretty_xml_string(
    xml_string: str,
    version: str = "1.0",
    encoding: str = "iso-8859-1",
    xml_declaration: bool = True,
) -> str:
    """Returns the prettified XML string."""
    dom = minidom.parseString(xml_string)
    pretty_xml_string = dom.toprettyxml(indent="   ", encoding=encoding).decode()
    if not xml_declaration:
        declaration = '<?xml version="%s" encoding="%s"?>' % (version, encoding)
        pretty_xml_string = pretty_xml_string.replace(declaration, "").strip()
    return pretty_xml_string


def output_xml_file(
    element: ET.Element,
    is_print_output: bool = True,
    filename: str = "output.xml",
    is_xml_declaration: bool = True,
    version: str = "1.0",
    encoding: str = "iso-8859-1",
) -> str:
    """Outputs the XML element to a file and/or prints it to the console."""
    xml_string = get_xml_string(element, encoding)
    pretty_xml_string = get_pretty_xml_string(
        xml_string, version, encoding, is_xml_declaration
    )
    if is_print_output:
        print(pretty_xml_string)
    if filename:
        write_file(filename, pretty_xml_string, encoding)

    return pretty_xml_string


# validate xml definition from json-schema schematic functions 

def validate_json(schema: Dict[str, Any], xml_definition: Dict[str, Any]) -> None:
    """Validates JSON data against a JSON schema file."""
    if not schema:
        print("JSON schema is empty.")
        return
    if not xml_definition:
        print("JSON XML definition is empty.")
        return
    try:
        jsonschema.validate(xml_definition, schema)
        print("JSON is valid against the schema.")
    except jsonschema.exceptions.ValidationError as e:
        print("JSON is not valid against the schema.")
        print(e)
