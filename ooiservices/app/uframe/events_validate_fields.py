"""
Events: Validate required event fields based on event type.
"""
# todo - Remove exception for calibration once it is added to uframe..
# todo - Remove exception for deployments once it is added to UI.

__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.common_tools import (get_event_types, is_instrument, is_platform, is_mooring)


def events_validate_all_required_fields_are_provided(event_type, data, action=None):
    """ Verify for the event_type and action, the required field have been provided in the input data.
    """
    try:
        # Calibration data create and update not yet supported in uframe, raise exception.
        if event_type == 'CALIBRATION_DATA':
            message = 'Event type %s \'create\' or \'update\' is not supported in uframe.' % event_type
            raise Exception(message)
        # Deployment event create and update not yet supported in UI; , raise exception.
        if event_type == 'DEPLOYMENT':
            message = 'Event type %s \'create\' or \'update\' is not supported yet in UI.' % event_type
            raise Exception(message)

        # Convert field values: - All field values are provided as type string, convert into target type.
        converted_data = convert_required_fields(event_type, data, action)

        # Get asset management event types
        valid_event_types = get_event_types()
        event_type = event_type.upper()
        if event_type not in valid_event_types:
            message = 'Valid event type is required to validate event fields. Invalid value: %s' % event_type
            raise Exception(message)

        # Get required fields and field types (from UI for uframe create event).
        required_fields, field_types = get_required_fields_and_types(event_type, action)
        if not required_fields:
            message = 'Event type %s action %s requires specific fields.' % (event_type, action)
            raise Exception(message)
        if not field_types:
            message = 'Event type %s action %s requires specific field types.' % (event_type, action)
            raise Exception(message)

        # Create integrationInfo dictionary or None when appropriate for 'INTEGRATION' event type.
        if event_type == 'INTEGRATION':
            integrationInto = process_integration_event(converted_data)
            converted_data['integrationInto'] = integrationInto

        # Create location dictionary for uframe when appropriate for LOCATION event type.
        elif event_type == 'LOCATION':
            location_dict = create_location_dict(converted_data, action)
            converted_data['location'] = location_dict
            required_fields.append('location')

        # Set location dictionary to None for ASSET_STATUS event type.
        elif event_type == 'ASSET_STATUS':
            converted_data['location'] = None

        # Verify required fields are present in the data and each field has input data of correct type.
        for field in required_fields:

            if event_type == 'INTEGRATION' and field == 'integrationInto':
                continue

            # Verify field is provided in data
            if field not in converted_data:
                message = 'required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'required field %s does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if converted_data[field] is not None:

                # 'string'
                if field_types[field] == 'string':
                    if not isinstance(converted_data[field], str) and not isinstance(converted_data[field], unicode):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)

                # 'int'
                elif field_types[field] == 'int':
                    if not isinstance(converted_data[field], int):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)

                # 'long'
                elif field_types[field] == 'long':
                    if not isinstance(converted_data[field], long):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)

                # 'dict'
                elif field_types[field] == 'dict':
                    if not isinstance(converted_data[field], dict):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)

                # 'float'
                elif field_types[field] == 'float':
                    if not isinstance(converted_data[field], float):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)

                # 'list or 'intlist' or 'floatlist'
                elif field_types[field] == 'list' or \
                     field_types[field] == 'intlist' or field_types[field] == 'floatlist':
                    if not isinstance(converted_data[field], list):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)
                # Error
                else:
                    message = 'required field %s provided, but value is undefined type %s' % (field, field_types[field])
                    raise Exception(message)

        # Determine if 'extra' fields are being provided in the data, if so, report in log.
        number_of_required_fields = len(required_fields)
        number_of_data_fields = len(converted_data.keys())
        extra_fields = []
        if number_of_data_fields != number_of_required_fields:
            data_fields = converted_data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)
        if extra_fields:
            message = 'data contains extra fields %s, ' % extra_fields
            message += 'correct and re-submit request to validate fields for %s %s event request.' % \
                       (action.upper(), event_type)
            current_app.logger.info(message)
            raise Exception(message)

        return converted_data

    except Exception as err:
        message = str(err)
        raise Exception(message)


# todo - Add CALIBRATION_DATA fields here.
# todo - Verify DEPLOYMENT fields here.
def get_required_fields_and_types(event_type, action):
    """ Get required fields and field types for event_type being processed.

    Event types are:
        'ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
        'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED',

        'RECOVERY' event type is not supported by uframe (at all).
        'CALIBRATION_DATA' event type creation and update is not supported by uframe.
        'DEPLOYMENT' event type creation and update is not supported by the UI.
    """
    required_fields = []
    field_types = {}
    valid_actions = ['create', 'update']
    try:
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: ACQUISITION
        #- - - - - - - - - - - - - - - - - - - - - - -
        if event_type == 'ACQUISITION':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'dataSource', 'tense', 'assetUid',
                       'purchasedBy', 'purchaseDate', 'deliveryDate',
                       'vendorIdentification', 'vendorPointOfContact',
                       'receivedFromVendorBy', 'authorizationNumber',
                       'authorizationForPayment', 'invoiceNumber', 'purchasePrice']
            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string',
                    'purchasedBy': 'string', 'purchaseDate': 'long', 'deliveryDate': 'long',
                    'vendorIdentification': 'string', 'vendorPointOfContact': 'string',
                    'receivedFromVendorBy': 'string', 'authorizationNumber': 'string',
                    'authorizationForPayment': 'string', 'invoiceNumber': 'string',
                    'purchasePrice': 'float'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: ASSET_STATUS
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'ASSET_STATUS':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'severity', 'reason', 'status', 'location',
                       'notes', 'dataSource', 'tense', 'assetUid']
            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string', 'location': 'dict', 'status': 'string',
                    'severity': 'int', 'reason': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: ATVENDOR
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'ATVENDOR':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'reason', 'vendorIdentification', 'authorizationNumber',
                       'authorizationForPayment', 'invoiceNumber', 'vendorPointOfContact',
                       'sentToVendorBy', 'receivedFromVendorBy',
                       'notes', 'dataSource', 'tense', 'assetUid']

            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string',
                    'reason': 'string', 'vendorIdentification': 'string', 'authorizationNumber': 'string',
                    'authorizationForPayment': 'string', 'invoiceNumber': 'string', 'vendorPointOfContact': 'string',
                    'sentToVendorBy': 'string', 'receivedFromVendorBy': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: CALIBRATION_DATA
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'CALIBRATION_DATA':
            message = 'event type CALIBRATION_DATA not currently supported in uframe.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: CRUISE_INFO
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'CRUISE_INFO':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'uniqueCruiseIdentifer',  'cruiseIdentifier', 'shipName',
                       'notes', 'dataSource', 'tense', 'assetUid']

            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string',
                    'uniqueCruiseIdentifer': 'string', 'cruiseIdentifier': 'string', 'shipName': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: DEPLOYMENT
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'DEPLOYMENT':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'dataSource', 'tense', 'assetUid',
                       'inductiveId', 'deployedBy', 'location', 'sensor', 'mooring', 'node',
                       'recoverCruiseInfo', 'recoveredBy', 'deploymentNumber', 'ingestInfo',
                       'referenceDesignator', 'versionNumber', 'deployCruiseInfo']

            field_types = {'eventName': 'string', 'eventId': 'int',
                            'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                            'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                            'tense': 'string', 'assetUid': 'string',
                            'inductiveId': 'string', 'deployedBy': 'string',
                            'location': 'dict', 'sensor': 'dict', 'mooring': 'dict', 'node': 'dict',
                            'recoverCruiseInfo': 'dict', 'recoveredBy': 'string',
                            'deploymentNumber': 'int', 'ingestInfo': 'list',
                            'referenceDesignator': 'dict', 'versionNumber': 'int', 'deployCruiseInfo': 'dict'
                           }

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: INTEGRATION
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'INTEGRATION':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'integrationInto', 'deploymentNumber', 'versionNumber', 'integratedBy',
                       'notes', 'dataSource', 'tense', 'assetUid']

            field_types = {
                            'eventName': 'string', 'eventId': 'int',
                            'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                            'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                            'tense': 'string', 'assetUid': 'string', 'location': 'string', 'status': 'string',
                            'integrationInto': 'string', 'deploymentNumber': 'int',
                            'versionNumber': 'int', 'integratedBy': 'string'
                          }

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: LOCATION
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'LOCATION':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'depth',  'longitude', 'latitude', 'orbitRadius',
                       'notes', 'dataSource', 'tense', 'assetUid']

            field_types = {'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string',
                    'depth': 'float', 'location': 'dict',
                    'longitude': 'float', 'latitude': 'float', 'orbitRadius': 'float'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: RETIREMENT
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'RETIREMENT':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'reason', 'disposition', 'retiredBy',
                       'notes', 'dataSource', 'tense', 'assetUid']

            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                    'tense': 'string', 'assetUid': 'string', 'location': 'string', 'status': 'string',
                    'reason': 'string', 'disposition': 'string', 'retiredBy': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: STORAGE
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'STORAGE':
            required_fields = ['buildingName', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'performedBy', 'physicalLocation', 'roomIdentification',
                       'shelfIdentification', 'dataSource', 'tense', 'assetUid']
            field_types = { 'buildingName': 'string', 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'performedBy': 'string',
                    'physicalLocation': 'string', 'roomIdentification': 'string',
                    'shelfIdentification': 'string', 'dataSource': 'string', 'tense': 'string', 'assetUid': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: UNSPECIFIED
        #- - - - - - - - - - - - - - - - - - - - - - -
        elif event_type == 'UNSPECIFIED':
            required_fields = ['eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                       'notes', 'dataSource', 'tense', 'assetUid']
            field_types = { 'eventName': 'string', 'eventId': 'int',
                    'eventStartTime': 'long', 'eventStopTime': 'long', 'eventType': 'string',
                    'lastModifiedTimestamp': 'long', 'notes': 'string', 'dataSource': 'string',
                     'tense': 'string', 'assetUid': 'string'}

        #- - - - - - - - - - - - - - - - - - - - - - -
        # Event type: Unknown - error.
        #- - - - - - - - - - - - - - - - - - - - - - -
        else:
            message = 'Unknown event type %s not currently supported in events_validate_fields.' % event_type
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Review action based field requirements for all event types.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if required_fields and field_types:
            update_additional_fields = ['eventId', 'lastModifiedTimestamp']
            if action == 'update':
                required_fields += update_additional_fields
                if 'eventId' not in field_types:
                    field_types['eventId'] = 'int'
                if 'lastModifiedTimestamp' not in field_types:
                    field_types['lastModifiedTimestamp'] = 'long'
            required_fields.sort()
        else:
            message = 'Failed to obtain required fields and field types for event type %s, action: %s' % \
                      (event_type, action)
            raise Exception(message)

        return required_fields, field_types

    except Exception as err:
        message = str(err)
        raise Exception(message)


def convert_required_fields(event_type, data, action=None):
    """ Verify for the event_type and action, the required fields have been provided in the input data.
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
    """
    converted_data = {}
    try:
        # Fields required (from UI) for uframe create event.
        verify_inputs(event_type, data, action)
        required_fields, field_types = get_required_fields_and_types(event_type, action)

        if not required_fields:
            message = 'Event type %s action %s requires specific fields.' % (event_type, action)
            raise Exception(message)
        if not field_types:
            message = 'Event type %s action %s requires specific field types.' % (event_type, action)
            raise Exception(message)

        if event_type == 'ASSET_STATUS':
            data['location'] = None

        # Verify required fields are present in the data and each field has input data of correct type.
        for field in required_fields:

            # Verify field is provided in data
            if field not in data:
                message = 'required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'required field %s does not have a defined field type value' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if data[field] is None:
                converted_data[field] = None

            elif data[field] is not None:
                # 'string'
                if field_types[field] == 'string':
                    if data[field] and len(data[field]) > 0:
                        tmp = str(data[field])
                        if not isinstance(tmp, str) and not isinstance(data[field], unicode):
                            message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                            raise Exception(message)
                        converted_data[field] = tmp
                    else:
                        converted_data[field] = None

                # 'int'
                elif field_types[field] == 'int':
                    try:
                        if data[field] and len(data[field]) > 0:
                            tmp = int(data[field])
                            if not isinstance(tmp, int):
                                message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                                raise Exception(message)
                            converted_data[field] = tmp
                        else:
                            converted_data[field] = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s)' % (field, field_types[field])
                        raise Exception(message)

                # 'long'
                elif field_types[field] == 'long':
                    try:
                        if data[field] and len(data[field]) > 0:
                            tmp = long(data[field])
                            if not isinstance(tmp, long):
                                message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                                raise Exception(message)
                            converted_data[field] = tmp
                        else:
                            converted_data[field] = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s)' % (field, field_types[field])
                        raise Exception(message)

                # 'float'
                elif field_types[field] == 'float':
                    try:
                        if data[field] and len(data[field]) > 0:
                            tmp = float(data[field])
                            if not isinstance(tmp, float):
                                message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                                raise Exception(message)
                            converted_data[field] = tmp
                        else:
                            converted_data[field] = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s)' % (field, field_types[field])
                        raise Exception(message)

                # 'dict'
                elif field_types[field] == 'dict':
                    continue
                    #message = 'Unknown dict field to convert: ', field
                    #raise Exception(message)

                # 'list'
                elif field_types[field] == 'list':
                    try:
                        tmp = data[field].strip()
                        if len(tmp) < 2:
                            message = 'Invalid value (%s) for list.' % data[field]
                            print '\n exception: ', message
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
                        message = 'required field %s provided, but type conversion error (type %s)' % (field, field_types[field])
                        raise Exception(message)

                    if not isinstance(tmp, list):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp

                elif field_types[field] == 'intlist' or field_types[field] == 'floatlist':
                    try:
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
                        message = 'required field %s provided, but type conversion error (type %s)' % (field, field_types[field])
                        raise Exception(message)
                    if not isinstance(tmp, list):
                        message = 'required field %s provided, but value is not of type %s' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp
                else:
                    message = 'required field %s provided, but value is undefined type %s' % (field, field_types[field])
                    raise Exception(message)

        return converted_data

    except Exception as err:
        message = str(err)
        raise Exception(message)


def verify_inputs(event_type, data, action):
    """ Simple error checking for input data.
    """
    valid_actions = ['create', 'update']
    try:
        # Check action is provided and valid.
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)

        # Check data is provided and of correct type.
        if not data:
            message = 'Field validation requires event type, data dict and a defined action; data is empty.'
            raise Exception(message)
        if not isinstance(data, dict):
            message = 'Field validation requires data to be of type dictionary.'
            raise Exception(message)

        # Verify valid event_type provided and valid.
        if not event_type:
            message = 'Field validation requires event_type to be provided, not empty.'
            raise Exception(message)
        if event_type not in get_event_types():
            message = 'Valid event type is required to validate event fields. Invalid value: %s' % event_type
            raise Exception(message)

    except Exception as err:
        message = str(err)
        raise Exception(message)


def process_integration_event(data):
    """ Process integration event data from UI to send to uframe.
    """
    rd = None
    integrationInto_dict = None
    try:
        # Get reference designator.
        if 'integrationInto' in data:
            rd = data['integrationInto']

        # If rd provided, process into integrationInto dictionary.
        if rd:
            integrationInto_dict = create_integrationInto(rd)
        return integrationInto_dict

        """
        # Prevent creation of integration event for non-existent deployment number for associated asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Deployment number.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get deployment number from data.
        deployment_number = None
        if 'deploymentNumber' in data:
            deployment_number = data['deploymentNumber']
        if deployment_number is None:
            message = 'Failed to get deploymentNumber value from INTEGRATION event.'
            raise Exception(message)

        # Get existing deployment numbers for this asset.
        current_deployment_numbers = None
        if 'deployment_numbers' in asset:
            current_deployment_numbers= asset['deployment_numbers']
        if current_deployment_numbers is None:
            message = 'Failed to get deployment_numbers from asset with uid: %d; ' % deployment_number
            message += 'cannot verify proposed deployment in integration event.'
            current_app.logger.info(message)
            raise Exception(message)

        # Verify the deployment number provided is an existing deployment number associated with this asset.
        if debug: print '\n debug -- current_deployment_numbers: ', current_deployment_numbers
        if deployment_number not in current_deployment_numbers:
            message = 'The proposed deployment number (%d) does not exist for asset with uid: %s' % \
                      (deployment_number, uid)
            current_app.logger.info(message)
            raise Exception(message)
        """

    except Exception as err:
        message = str(err)
        raise Exception(message)


def create_integrationInto(rd):
    """ Creates dictionary for integrationInto value.
    "integrationInto" : {
        "node" : "RID26",
        "subsite" : "CP01CNSM",
        "sensor" : "04-VELPTA000"
      }
    """
    node = ''
    sensor = ''
    try:
        if rd is None:
            return None
        if is_instrument(rd):
            subsite, node, sensor = rd.split('-', 2)
        elif is_platform(rd):
            subsite, node = rd.split('-')
        elif is_mooring(rd):
            subsite = rd
        else:
            message = 'Invalid reference designator to integrate into; provide valid reference designator.'
            raise Exception(message)

        template = {
        'node' : node,
        'subsite' : subsite,
        'sensor' : sensor
        }
        return template
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rd_from_integrationInto(data):
    """ Get reference designator from INTEGRATION event integrationInto dictionary field.
    """
    required_attributes = ['subsite', 'node', 'sensor']
    try:
        rd = None
        if not data:
            message = 'No integrationInto data provided to determine reference designator.'
            raise Exception(message)
        if not isinstance(data, dict):
            message = 'The integrationInto data provided not in form of a dictionary.'
            raise Exception(message)

        for item in required_attributes:
            if item not in data:
                message = 'Attribute \'%s\' not provided in integrationInto dictionary,' % item
                message += ' cannot produce reference designator.'
                raise Exception(message)

        subsite = data['subsite']
        if not subsite:
            return None
        node = data['node']
        sensor = data['sensor']

        # Construct rd from data
        rd = subsite
        if node:
            rd += '-' + node
        if sensor:
            rd += '-' + sensor
        return rd
    except Exception as err:
        message = str(err)
        raise Exception(message)


def events_validate_user_required_fields_are_provided(event_type, valid_data, action='create'):
    """ Verify for the event_type and action, the required user fields have been populated in the input data.
    """
    try:
        # Get asset management event types
        valid_event_types = get_event_types()
        event_type = event_type.upper()
        if event_type not in valid_event_types:
            message = 'Valid event type is required to validate event fields. Invalid value: %s' % event_type
            raise Exception(message)

        # Get list of fields user must provide for an event type create or update
        user_fields = get_user_fields_populated(event_type, action)

        # Verify required fields are present in the data and each field has input data of correct type.
        for field in user_fields:

            # Verify field is provided in data (get display names in here)
            if field not in valid_data:
                message = 'required user field %s not provided in data.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if valid_data[field] is None:
                message = 'required field \'%s\' must be populated.' % field
                raise Exception(message)
        return

    except Exception as err:
        message = str(err)
        raise Exception(message)

def get_user_fields_populated(event_type, action):
    """ For an event type and action, get fields the user shall populate. Return list.
    """
    user_populated_fields = ['eventName']
    event_fields = []
    try:
        # Event type: INTEGRATION
        if event_type == 'INTEGRATION':
            # For action(s): create and update
            event_fields = ['versionNumber', 'deploymentNumber']

        # Event type: CRUISE_INFO
        elif event_type == 'CRUISE_INFO':
            event_fields = ['uniqueCruiseIdentifer', 'shipName', 'cruiseIdentifier']

        if event_fields:
            user_populated_fields = user_populated_fields + event_fields
        return user_populated_fields
    except Exception as err:
        message = str(err)
        raise Exception(message)


def create_location_dict(data, action):
    """ Verify fields to create location have been provided in data; create output dictionary.

    "location" : {
        "depth" : 551.27,
        "location" : [ -70.8125, 40.467731 ],
        "latitude" : 40.467731,
        "longitude" : -70.8125,
        "orbitRadius" : 0.0
      },
    """
    required_fields = ['depth', 'latitude', 'longitude', 'orbitRadius']
    try:
        if not data:
            message = 'Failed to receive data to create location dictionary for ufame.'
            raise Exception(message)

        for item in required_fields:
            if item not in data:
                message = 'Failed to receive required field \'%s\' in request data.'
                raise Exception(message)

        depth = data['depth']
        longitude = data['longitude']
        latitude = data['latitude']
        orbitRadius = data['orbitRadius']
        if latitude is None and longitude is not None:
            message = 'Both latitude and longitude must be populated (not just longitude).'
            raise Exception(message)
        if latitude is not None and longitude is None:
            message = 'Both latitude and longitude must be populated, (not just latitude).'
            raise Exception(message)

        if action == 'create':
            return None

        # Build and return location dictionary
        location_dict = {}
        location_dict['depth'] = depth
        location = [longitude, latitude]
        location_dict['location'] = location
        location_dict['latitude'] = latitude
        location_dict['longitude'] = longitude
        location_dict['orbitRadius'] = orbitRadius
        return location_dict
    except Exception as err:
        message = str(err)
        raise Exception(message)
