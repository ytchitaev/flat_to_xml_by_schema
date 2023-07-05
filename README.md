# flat_to_xml_by_schema

This project demonstrates how to convert a flat dataset to a basic XML using a XML definition defined in JSON metadata using ElementTree python library.

## Use

1. Clone the repository or download the project files.
2. `create_venv.ps1` to create venv from requirements.
5. Run `main.py` for example implementation and adapt project as required.

## Metadata

- `dataset.py` - Example input dataset, this should be replaced by a database or dataframe source in an actual implementation.
- `xml_definition.json` - The header / row level definition that should be extracted from the input dataset.
- `schema.json` - Schema definition of `xml_declaration.json`.
- `xml_declaration.json` - Declaration such as encoding and XML version for the XML output.

## Implementation

- Metadata assumes you will have `header` defined attributes / values that will be built once in the XML structure and `row` values that will be iterates per incoming flat dataset row.
- `@{dataset_column_value}` convention is used to populate row-wise values from `row` defined fields in the XML defintion file.
- `#NULL#` placeholder vlaues from the input flat datasets represent fields that should not be generated in XML (as opposed to empty values which are sent as empty values).
- When sending empty element values (not `#NULL#` values which are not sent at all), ElementTree uses `<Name/>` self closing elements instead of empty elements `<Name></Name>` by default.
- Schema only supports basic attribute / value structures. More complex XML elements like data types, normalisation and substition groups are not currently implemented.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
