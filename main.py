import generate_xml
from dataset import dataset

# read json-schema validation
schema = generate_xml.read_json_file("schema.json")

# read mapping
xml_definition = generate_xml.read_json_file("xml_definition.json")
xml_declaration = generate_xml.read_json_file("xml_declaration.json")

# validate declaration against json schema
generate_xml.validate_json(schema, xml_definition)

# print xml / construct output xml
xml_root = generate_xml.build_xml(xml_definition, dataset)
xml_formatted = generate_xml.output_xml_file(
    element=xml_root,
    is_print_output=True,
    filename="output.xml",
    is_xml_declaration=True,
    version=xml_declaration["version"],
    encoding=xml_declaration["encoding"]
)
