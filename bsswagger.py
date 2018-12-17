import yaml
import json
import logging 
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)



class BsSwagger():

    def __init__(self, filename, debug=False):
        self.filename = filename
        self.swagger = self._get_swagger(filename)
        self.request_schema = None 
        self.response_schema = None
        self.logger = self._build_logger(debug)
        self.ref = {}
        self.parameters = {}
        self.schema = {"body":{"schema":[]}}
        self.wrong_type = []
        self.ref_list = []
    def _get_swagger(self, filename):
        with open('swagger.yaml') as f:
            return yaml.load(f)
       
    def _build_logger(self, debug):
        level = 9 if debug else 20
        level=logging.DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        return logger

    def get_schema(self, path=None, method=None):
        schema_dict = self.swagger['paths']
        if path:
            schema_dict = schema_dict.get(path)
            if not schema_dict:
                msg = "specified path not found in swagger"
                raise ParsingException(msg)
        schema_dict = self._find_ref(schema_dict)
        self.request_schema = schema_dict
        if method:
            methods = ('get','post','patch','delete')
            if method not in methods:
                msg = "{method} not a valid rest method, choose {methods}"
                raise ParsingException(msg)
            else:
                schema_dict= schema_dict[method]
        schema_dict = self._find_ref(schema_dict)
        self.request_schema = schema_dict
        keys = ("body","properties",)
        self._check_object(keys, schema_dict)
        print("final schema")
        print(json.dumps(self.schema, indent=4))
        #self._check_object(keys, schema_dict)
        #self.request_schema = schema_dict['parameters'][0]['schema']#fix when understand
        #self.response_schema = schema_dict['responses']
        return schema_dict
   
    def _check_object(self, json_keys, swagger_obj):
        keywords = ["oneOf","anyOf","allOf","not"]
        if any(word in swagger_obj.keys() for word in keywords):
            swagger_obj = self.replace_keywords(swagger_obj)
        for key in swagger_obj.keys():
            if key == 'requestBody':
                try:
                    swagger_obj=swagger_obj['requestBody']['content']['application/json']# should be variable
                except KeyError:
                    msg='content and content type are required arguments in request_body' 
                    raise InvalidSwagger(msg)
            if key == 'parameters':
                self._append_schema(json_keys, swagger_obj[key][0])
            if key == 'schema':
                self._append_schema(json_keys, swagger_obj[key])             

    def _append_schema(self, keys_tuple, schema):
        keywords = ["oneOf","anyOf","allOf","not"]
        for key, value in schema.items():
            if key == 'ref':
                self._append_schema(keys_tuple, self.ref[value])
            elif key in keywords:    
                self.replace_keywords(keys_tuple, key, value)
            elif key == 'required':
                required = schema['required']
                self._schema_data_append(keys_tuple + (key,), required)
            elif key == 'properties':
                self._append_schema(keys_tuple , value)
                #self._schema_data_append(keys_tuple,self.schema, 'properties', value)
            elif key == 'type':
                if value in ('integer', 'string'):
                    #new_key_tuple += key_tuple + (key,)
                    self._schema_data_append(keys_tuple,{key:value})
                elif value  in ('object', 'array'):
                    #new_key_tuple = keys_tuple + (key,)
                    self._schema_data_append(keys_tuple,{key:value})
                    #self._append_schema(keys_tuple, value)
            elif key in ['format','name','enum']:
                    #new_key_tuple += key_tuple + (key,)
                    self._schema_data_append(keys_tuple+(key,), value)
            else:
                if type(value)==dict:
                #self._schema_data_append(keys_tuple+(key,) ,self.schema, value)
                    self._append_schema(keys_tuple+(key,), value)

    def replace_keywords(self, keys_tuple, keyword, value):
        print("replace", keys_tuple, value)
        if keyword == 'allOf':
            for i in value:
                print("i",keys_tuple, i)
                self._append_schema(keys_tuple, i)
        else:
            raise BsSwaggerException("not yet supported")

    def _schema_data_append(self,  keys_tuple, data):
        print("keys_tuples", keys_tuple, "val", data)
        dic = self.schema
        for key in keys_tuple[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys_tuple[-1]]=data
        print('dic',dic[keys_tuple[-1]])
        print("self", self.schema)
    
    def _check_for_requestBody(swagger_dict):
        if swagger_dict.get['requestBody]']:
            #content is a requirerd element of requestBody object
            try:
                swagger_dict = swagger_dict['requestBody']['content']
            except KeyError:
                raise InvalidSwagger('request body must include content object')
            return swagger_dict
        
    def _find_ref(self, swagger):
        ref_key = None
        self.logger.debug("parsing {swagger} for ref")
        if type(swagger) == list:
            self.logger.debug("swagger is list: {swagger}")
            swagger = [self._find_ref(i) for i in swagger]
        if type(swagger) == dict:
            if "$ref" in swagger.keys():
                ref_value = swagger['$ref']
                self.logger.debug("$ref found in {swagger}")
                ref_key = self._resolve_ref(ref_value)
                self.logger.debug("resolved {ref_value} to {swagger}")
            else:
                for key,v in swagger.items():
                    if type(v) in (list, dict):
                        swagger[key] = self._find_ref(v)
        if ref_key:
            return {"ref": ref_key}
        else:
            return swagger
            
    def _resolve_ref(self, ref_value):
        same_file = False
        if ref_value.startswith('#'):
            new_keys = ref_value.lstrip('#').split("/")[1:]
            same_file=True
        elif "#" in ref_value:
            file_nm, new_keys = ref_value.split("#")
            self.logger.debug("opening file {file_nm}")
        else:
            file_nm = ref_value
        if same_file:
            swagger = self.swagger
        else:
            swagger = self._get_swagger(file_nm)
        for key in new_keys:
            swagger = swagger[key]
        key_name = "_".join(new_keys)
            
        self._find_ref(swagger)
        self.logger.debug("resolving {ref_value} to {swagger}")
        self.ref[key_name] = swagger
        return key_name

    def check_request(self, request_json):
        #rq request schema
        if not self.request_schema:
            raise NotYetDefined
        rqs = self.request_schema
        self.logger.debug("request_schema: {rqs}")
        self.request_required = rqs["required"]
        missing = self._check_required(request_json, self.request_required)
        if missing:
            raise InvalidRequest(missing)
        #prop request parameter properties
        prop = rqs['properties']
        self.logger.debug("start types")
        if self._check_types(request_json, self.request_schema):
            if self.wrong_type:
                mismatch = ""
                for i in self.wrong_type:
                    mismatch += ", {i[0]} type should be {i[1]}"
            raise TypeMismatch(mismatch)
        return True
    
    def _check_required(self, json, reqs):
        #reqs required list
        self.logger.debug("required list: {reqs}")
        missing = []
        for req in reqs:
            if json.get(req):
                pass
            else:
                missing.append(req)
        self.logger.debug("missing: {missing}")
        return missing

    def _check_types(self, json, prop, *args):
        if args:
            location = ".".join(args)
        else:
            location = "The whole thing"
        self.logger.debug("location: {location}, json {json}, prop{prop} ")
        if prop['type'] == 'object':
            if type(json) != dict:
                self.wrong_type.append((location, "object"))
            else:
                self._itr_object_types(json, prop, *args) 
        elif prop['type'] == "array":
            if type(json) != list:
                self.wrong_type.append((location, "array"))
            else:
                self._itr_array_types(json, prop, *args)
        elif prop['type'] == 'string':
            if type(json) != str:
                self.wrong_type.append((location, "string"))
                #check enum here
            else:
                self.logger.debug("{location} validated string")
                if prop.get('enum'):
                    enum = prop['enum']
                    self.logger.debug("checking enum {enum}")
                    if json not in enum:
                        self.wrong_type.append((location, "in enum: {enum}"))
                        
        elif prop['type'] == 'integer':
            if type(json) != int:
                self.wrong_type.append((location, "integer"))
            else:
                self.logger.debug("{location} validated int")
        return self.wrong_type

    def _itr_object_types(self, obj, prop, *args):
        self.logger.debug("pasrse dict")
        for k, v in prop['properties'].items():
            self.logger.debug("pasrse {k}")
            bargs = args +(k,)
            self.logger.debug("args: {args} bargs: {bargs}")
            self._check_types(obj[k], v, *args +(k,))
        return 

    def _itr_array_types(self, array, prop, *args):
        for idx,i  in enumerate(array):
            self._check_types(i, prop['items'],*args + ("index [{idx}]",))
        return

class BsSwaggerException(Exception):
    def __init__(self,  msg=None):
        self.msg = msg
        if msg is None:
            # Set some default useful error message
            msg = "BsSwagger encountered and error"

class InvalidSwagger(BsSwaggerException):
    def __init__(self, msg):
        self.msg="parsing failed: {msg}"
        super(BsSwaggerException, self).__init__(self.msg)

class ParsingException(BsSwaggerException):
    def __init__(self, msg):
        self.msg="parsing failed: {msg}"
        super(BsSwaggerException, self).__init__(self.msg)

class ValidationFailed(BsSwaggerException):
    def __init__(self, issues):
        self.msg="request is invalid due to the following errors: {issues}"
        super(BsSwaggerException, self).__init__(self.msg)

class MissingElement(ValidationFailed):
    def __init__(self, missing):
        self.msg="request is invalid due to the following missing elements: {missing}"
        super(ValidationFailed, self).__init__(self.msg)

class TypeMismatch(ValidationFailed):
    def __init__(self, mismatch):
        self.msg="request is invalid due to the following type issues {mismatch}"
        super(ValidationFailed, self).__init__(self.msg)

if __name__=="__main__":
    from datetime import datetime
    start_get = datetime.now()
    bs = BsSwagger('swagger.yaml', debug = True)
    bs.get_schema('/pet','post')  #get method from header!
    stop_get = datetime.now()
    #with open('request_post.json') as f:
    #    request = json.load(f)
    #start_validate = datetime.now()
    #request_json = json.dumps(request, indent = 4)
    ##print(f"request: {request}")
    #bs.check_request(request)
    #stop_validate = datetime.now()
    ##print(json.dumps(bs.request_schema,indent=4))
    #print("good Request")
    #print("get",stop_get-start_get)
    #print("validate",stop_validate-start_validate)
