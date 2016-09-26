"""
Asset Management - Common conversion of UI input for events and assets.
"""
__author__ = 'Edna Donoughe'
import ast


def convert_ui_data(data, required_fields, field_types):
    """ Convert string values to target type for field. Dictionary processing performed by caller.
    """
    debug = False
    converted_data = {}
    try:
        if debug: print '\n debug -- entered convert_ui_data...'
        # Verify required fields are present in the data and each field has input data of correct type.
        for field in required_fields:
            if debug: print '\n debug -- field: %s' % field
            # Verify field is provided in data
            if field not in data:
                message = 'Required field \'%s\' not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'Required field \'%s\' does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if data[field] is None:
                converted_data[field] = None

            elif data[field] is not None:
                # 'string'
                if field_types[field] == 'string':
                    if not isinstance(data[field], str) and not isinstance(data[field], unicode):
                            message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                            raise Exception(message)
                    if data[field] and len(data[field]) > 0:
                        if debug: print '\n before encode...'
                        #tmp = str(data[field])
                        tmp = str((data[field]).encode('utf-8'))
                        if not isinstance(tmp, str) and not isinstance(tmp, unicode):
                            message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                            raise Exception(message)
                        converted_data[field] = tmp
                    else:
                        converted_data[field] = None

                # 'int'
                elif field_types[field] == 'int':
                    try:
                        if isinstance(data[field], int):
                            converted_data[field] = data[field]
                        else:
                            if data[field] and len(data[field]) > 0:
                                tmp = int(data[field])
                                if not isinstance(tmp, int):
                                    message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                                    raise Exception(message)
                                converted_data[field] = tmp
                            else:
                                converted_data[field] = None
                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                # 'long'
                elif field_types[field] == 'long':
                    try:
                        if isinstance(data[field], long) or isinstance(data[field], int):
                            converted_data[field] = long(data[field])
                        else:
                            if data[field] and len(data[field]) > 0:
                                tmp = long(data[field])
                                if not isinstance(tmp, long):
                                    message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                                    raise Exception(message)
                                converted_data[field] = tmp
                            else:
                                converted_data[field] = None
                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                # 'float'
                elif field_types[field] == 'float':
                    try:
                        if isinstance(data[field], float):
                            converted_data[field] = data[field]
                        else:
                            if data[field] and len(data[field]) > 0:
                                tmp = float(data[field])
                                if not isinstance(tmp, float):
                                    message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                                    raise Exception(message)
                                converted_data[field] = tmp
                            else:
                                converted_data[field] = None
                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                # 'dict'
                elif field_types[field] == 'dict':
                    converted_data[field] = data[field]
                    #message = 'Unknown dict field to convert: ', field
                    #raise Exception(message)
                    continue

                # 'bool'
                elif field_types[field] == 'bool':
                    try:
                        value = str(data[field])
                        if not value:
                            message = 'Boolean value provided is empty; unable to convert asset field %s' % field
                            raise Exception(message)

                        if value.lower() == 'true':
                            converted_data[field] = True
                        else:
                            converted_data[field] = False
                    except Exception as err:
                        message = str(err)
                        raise Exception(message)

                    if not isinstance(converted_data[field], bool):
                        message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)

                # 'list'
                elif field_types[field] == 'list':
                    try:
                        if isinstance(data[field], list):
                            tmp = data[field]
                        else:
                            tmp = data[field].strip()
                            if len(tmp) < 2:
                                message = 'Invalid value (%s) for list.' % data[field]
                                raise Exception(message)
                            if len(tmp) == 2:
                                if '[' in data[field] and ']' in data[field]:
                                    tmp = []
                            else:
                                if '[' in data[field]:
                                    tmp = tmp.replace('[', '')
                                if ']' in data[field]:
                                    tmp = tmp.replace(']', '')
                                tmp = tmp.strip()
                                if ',' not in tmp:
                                    tmp = [int(tmp)]
                                elif ',' in tmp:
                                    subs = tmp.split(',')
                                    newtmp = []
                                    for sub in subs:
                                        sub = sub.strip()
                                        if sub:
                                            if '.' in sub:
                                                val = float(sub)
                                                newtmp.append(val)
                                            else:
                                                val = int(sub)
                                                newtmp.append(val)
                                    tmp = newtmp
                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                    if not isinstance(tmp, list):
                        message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp

                elif field_types[field] == 'dictlist':
                    try:
                        field_type_text = 'list of dictionaries'
                        if isinstance(data[field], list):
                            tmp = data[field]
                        else:
                            tmp = ast.literal_eval(data[field])
                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (not a %s).' % \
                                  (field, field_types[field])
                        raise Exception(message)

                    if not isinstance(tmp, list):
                        message = 'Required field \'%s\' provided, but value is not a %s.' % (field, field_type_text)
                        raise Exception(message)
                    converted_data[field] = tmp

                elif field_types[field] == 'intlist' or field_types[field] == 'floatlist':

                    #===============================================
                    field_type_text = 'list of integers.'
                    try:
                        if field_types[field] == 'intlist':
                            field_type_text = 'list of integer values'
                        else:
                            field_type_text = 'list of float values'
                        if isinstance(data[field], list):
                            tmp = data[field]
                        else:
                            tmp = data[field].strip()
                            if len(tmp) < 2:
                                message = 'Invalid input value (%s) for list.' % data[field]
                                raise Exception(message)
                            if len(tmp) == 2:
                                if '[' in data[field] and ']' in data[field]:
                                    tmp = []
                            else:
                                if '[' in data[field]:
                                    tmp = tmp.replace('[', '')
                                if ']' in data[field]:
                                    tmp = tmp.replace(']', '')
                                tmp = tmp.strip()
                                if ',' not in tmp:
                                    if field_types[field] == 'floatlist':
                                        tmp = [float(tmp)]
                                    else:
                                        tmp = [int(tmp)]
                                elif ',' in tmp:
                                    subs = tmp.split(',')
                                    newtmp = []
                                    for sub in subs:
                                        sub = sub.strip()
                                        if sub:
                                            if field_types[field] == 'floatlist':
                                                val = float(sub)
                                                newtmp.append(val)
                                            else:
                                                val = int(sub)
                                                newtmp.append(val)

                                    tmp = newtmp

                    except:
                        message = 'Required field \'%s\' provided, but type conversion error (not a %s).' % \
                                  (field, field_type_text)
                        raise Exception(message)
                    #===============================================
                    if not isinstance(tmp, list):
                        message = 'Required field \'%s\' provided, but value is not %s.' % (field, field_type_text)
                        raise Exception(message)
                    converted_data[field] = tmp
                elif field_types[field] == 'multiple':
                    try:
                        if isinstance(data[field], list) or isinstance(data[field], float):
                                tmp = data[field]
                        else:
                            # convert the data
                            tmp = ast.literal_eval(data[field])
                            if isinstance(tmp, list):
                                converted_data[field] = tmp
                            elif isinstance(tmp, float):
                                converted_data[field] = tmp
                            else:
                                message = 'Field \'%s\' value is not of type list or float.' % field
                                raise Exception(message)
                    except Exception as err:
                        message = 'Required field \'%s\' provided, but type conversion error. %s' % (field, str(err))
                        raise Exception(message)
                    #converted_data[field] = tmp
                else:
                    message = 'Field \'%s\' has unknown field type provided.' % field
                    raise Exception(message)

        if debug: print '\n debug -- exit convert_ui_data...'
        return converted_data
    except Exception as err:
        message = str(err)
        raise Exception(message)

