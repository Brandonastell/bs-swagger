import yaml
import json
import logging 
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)



class BsSwagger():

    def __init__(self, filename, debug=False):
        self.filename = filename
        self.swagger = self._get_swagger(filename)
        self.schema = None
        self.request_required = None
        self.request_schema = None 
        self.response_schema = None
        self.logger = self._build_logger(debug)
        self.wrong_type = []

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
        if method:
            methods = ('get','post','patch','delete')
            if method not in methods:
                msg = f"{method} not a valid rest method, choose {methods}"
                raise ParsingException(msg)
            schema_dict= schema_dict[method]
        schema_json = json.dumps(schema_dict, indent=2)
        self.logger.debug(f"schema :{schema_json} with ref")
        schema_dict = self._find_ref(schema_dict)
        self.request_schema = schema_dict
        self.logger.debug(f"initial schema {schema_json}")
        self.request_schema = schema_dict['parameters'][0]['schema']#fix when understand
        self.response_schema = schema_dict['responses']
        return schema_dict
        
    def _find_ref(self, swagger):
        self.logger.debug(f"parsing {swagger} for ref")
        if type(swagger) == list:
            self.logger.debug(f"swagger is list: {swagger}")
            swagger = [self._find_ref(i) for i in swagger]
        if type(swagger) == dict:
            if "$ref" in swagger.keys():
                ref_value = swagger['$ref']
                self.logger.debug(f"$ref found in {swagger}")
                swagger = self._resolve_ref(ref_value)
                self.logger.debug(f"resolved {ref_value} to {swagger}")
            else:
                for key,v in swagger.items():
                    if type(v) in (list, dict):
                        swagger[key] = self._find_ref(v)
        return swagger
            
    def _resolve_ref(self, ref_value):
        same_file = False
        if ref_value.startswith('#'):
            new_keys = ref_value.lstrip('#').split("/")[1:]
            same_file=True
        elif "#" in ref_value:
            file_nm, new_keys = ref_value.split("#")
            self.logger.debug(f"opening file {file_nm}")
        else:
            file_nm = ref_value
        if same_file:
            swagger = self.swagger
        else:
            swagger = self._get_swagger(file_nm)
        for key in new_keys:
            swagger = swagger[key]
        self._find_ref(swagger)
        self.logger.debug(f"resolving {ref_value} to {swagger}")
        return swagger

    def check_request(self, request_json):
        #rq request schema
        if not self.request_schema:
            raise NotYetDefined
        rqs = self.request_schema
        self.logger.debug(f"request_schema: {rqs}")
        self.request_required = rqs["required"]
        missing = self._check_required(request_json, self.request_required)
        if missing:
            raise InvalidRequest(missing)
        #prop request parameter properties
        prop = rqs['properties']
        self.logger.debug(f"start types")
        if self._check_types(request_json, self.request_schema):
            if self.wrong_type:
                mismatch = ""
                for i in self.wrong_type:
                    mismatch += f", {i[0]} type should be {i[1]}"
            raise TypeMismatch(mismatch)
        return True
    
    def _check_required(self, json, reqs):
        #reqs required list
        self.logger.debug(f"required list: {reqs}")
        missing = []
        for req in reqs:
            if json.get(req):
                pass
            else:
                missing.append(req)
        self.logger.debug(f"missing: {missing}")
        return missing

    def _check_types(self, json, prop, *args):
        if args:
            location = ".".join(args)
        else:
            location = "The whole thing"
        self.logger.debug(f"location: {location}, json {json}, prop{prop} ")
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
                self.logger.debug(f"{location} validated string")
                if prop.get('enum'):
                    enum = prop['enum']
                    self.logger.debug(f"checking enum {enum}")
                    if json not in enum:
                        self.wrong_type.append((location, f"in enum: {enum}"))
                        
        elif prop['type'] == 'integer':
            if type(json) != int:
                self.wrong_type.append((location, "integer"))
            else:
                self.logger.debug(f"{location} validated int")
        return self.wrong_type

    def _itr_object_types(self, obj, prop, *args):
        self.logger.debug("pasrse dict")
        for k, v in prop['properties'].items():
            self.logger.debug(f"pasrse {k}")
            bargs = args +(k,)
            self.logger.debug(f"args: {args} bargs: {bargs}")
            self._check_types(obj[k], v, *args +(k,))
        return 

    def _itr_array_types(self, array, prop, *args):
        for idx,i  in enumerate(array):
            self._check_types(i, prop['items'],*args + (f"index [{idx}]",))
        return

class BsSwaggerException(Exception):
    def __init__(self,  msg=None):
        self.msg = msg
        if msg is None:
            # Set some default useful error message
            msg = "BsSwagger encountered and error"

class ParsingException(BsSwaggerException):
    def __init__(self, msg):
        self.msg=f"parsing failed: {msg}"
        super(BsSwaggerException, self).__init__(self.msg)

class ValidationFailed(BsSwaggerException):
    def __init__(self, issues):
        self.msg=f"request is invalid due to the following errors: {issues}"
        super(BsSwaggerException, self).__init__(self.msg)

class MissingElement(ValidationFailed):
    def __init__(self, missing):
        self.msg=f"request is invalid due to the following missing elements: {missing}"
        super(ValidationFailed, self).__init__(self.msg)

class TypeMismatch(ValidationFailed):
    def __init__(self, mismatch):
        self.msg=f"request is invalid due to the following type issues {mismatch}"
        super(ValidationFailed, self).__init__(self.msg)

if __name__=="__main__":
    from datetime import datetime
    start_get = datetime.now()
    bs = BsSwagger('swagger.yaml', debug = True)
    bs.get_schema('/pet','post')  #get method from header!
    stop_get = datetime.now()
    with open('request_post.json') as f:
        request = json.load(f)
    start_validate = datetime.now()
    request_json = json.dumps(request, indent = 4)
    #print(f"request: {request}")
    bs.check_request(request)
    stop_validate = datetime.now()
    #print(json.dumps(bs.request_schema,indent=4))
    print("good Request")
    print("get",stop_get-start_get)
    print("validate",stop_validate-start_validate)
