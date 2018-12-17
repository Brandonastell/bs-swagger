keys_tuple ('body', 'properties') val {'name': 'body'}
keys_tuple ('body', 'properties', 'required') val True
keys_tuple ('body', 'properties', 'schema') val {'type': 'object'}
keys_tuple ('body', 'properties', 'schema', 'required') val ['name', 'photoUrls']
keys_tuple ('body', 'properties', 'schema', 'id') val {'type': 'integer'}
keys_tuple ('body', 'properties', 'schema', 'id') val {'format': 'int64'}
keys_tuple ('body', 'properties', 'schema') val {'name': {'type': 'string', 'example': 'doggie'}}
keys_tuple ('body', 'properties', 'schema', 'othername') val {'type': 'object'}
keys_tuple ('body', 'properties', 'schema', 'othername') val {'name': {'type': 'string', 'example': 'doggie'}}
keys_tuple ('body', 'properties', 'schema', 'othername', 'id') val {'type': 'integer'}
keys_tuple ('body', 'properties', 'schema', 'othername', 'id') val {'format': 'int64'}
keys_tuple ('body', 'properties', 'schema', 'othername', 'mothername') val {'type': 'object'}
keys_tuple ('body', 'properties', 'schema', 'othername', 'mothername') val {'name': {'type': 'string', 'example': 'doggie'}}
keys_tuple ('body', 'properties', 'schema', 'othername', 'mothername', 'id') val {'type': 'integer'}
keys_tuple ('body', 'properties', 'schema', 'othername', 'mothername', 'id') val {'format': 'int64'}
keys_tuple ('body', 'properties', 'schema', 'photoUrls') val {'type': 'array'}
keys_tuple ('body', 'properties', 'schema', 'photoUrls', 'xml') val {'name': 'photoUrl'}
keys_tuple ('body', 'properties', 'schema', 'photoUrls', 'items') val {'type': 'string'}
keys_tuple ('body', 'properties', 'schema', 'tags') val {'type': 'array'}
keys_tuple ('body', 'properties', 'schema', 'tags', 'xml') val {'name': 'tag'}
keys_tuple ('body', 'properties', 'schema', 'tags', 'items') val {'type': 'object'}
keys_tuple ('body', 'properties', 'schema', 'tags', 'items', 'id') val {'type': 'integer'}
keys_tuple ('body', 'properties', 'schema', 'tags', 'items', 'id') val {'format': 'int64'}
keys_tuple ('body', 'properties', 'schema', 'tags', 'items') val {'name': {'type': 'string'}}
keys_tuple ('body', 'properties', 'schema', 'tags', 'items', 'xml') val {'name': 'Tag'}
keys_tuple ('body', 'properties', 'schema', 'status') val {'type': 'string'}
keys_tuple ('body', 'properties', 'schema', 'status') val {'enum': ['available', 'pending', 'sold']}
keys_tuple ('body', 'properties', 'schema', 'xml') val {'name': 'Pet'}
final schema
{
    "body": {
        "schema": [],
        "properties": {
            "name": "body",
            "required": true,
            "schema": {
                "name": {
                    "type": "string",
                    "example": "doggie"
                },
                "othername": {
                    "name": {
                        "type": "string",
                        "example": "doggie"
                    },
                    "id": {
                        "format": "int64"
                    },
                    "mothername": {
                        "name": {
                            "type": "string",
                            "example": "doggie"
                        },
                        "id": {
                            "format": "int64"
                        }
                    }
                },
                "photoUrls": {
                    "type": "array",
                    "xml": {
                        "name": "photoUrl"
                    },
                    "items": {
                        "type": "string"
                    }
                },
                "tags": {
                    "type": "array",
                    "xml": {
                        "name": "tag"
                    },
                    "items": {
                        "name": {
                            "type": "string"
                        },
                        "xml": {
                            "name": "Tag"
                        }
                    }
                },
                "status": {
                    "enum": [
                        "available",
                        "pending",
                        "sold"
                    ]
                },
                "xml": {
                    "name": "Pet"
                }
            }
        }
    }
}
