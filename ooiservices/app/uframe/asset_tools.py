#!/usr/bin/env python

"""
Asset Management - Assets: Supporting functions.
"""
__author__ = 'Edna Donoughe'

from flask import (current_app)
from ooiservices.app import cache
from copy import deepcopy
from ooiservices.app.uframe.stream_tools import get_stream_list
from ooiservices.app.uframe.vocab import (get_vocab, get_vocab_dict_by_rd,
                                          get_rs_array_name_by_rd, get_display_name_by_rd)
from ooiservices.app.uframe.uframe_tools import (get_assets_from_uframe, uframe_get_asset_by_id, uframe_get_asset_by_uid)
from ooiservices.app.uframe.common_tools import (get_asset_classes, get_supported_asset_types, get_location_fields,
                                                 get_asset_type_display_name)
from ooiservices.app.uframe.asset_cache_tools import (get_asset_rds_cache, asset_rds_cache_update)

import datetime as dt
from operator import itemgetter
CACHE_TIMEOUT = 172800
STREAM_CACHE_TIMEOUT = 36000

#import json
#from ooiservices.app.uframe.common_tools import (get_asset_type_by_rd, get_uframe_asset_type)
#from ooiservices.app.uframe.vocab import (get_rs_array_name_by_rd, get_display_name_by_rd)
#from ooiservices.app.uframe.controller import dfs_streams
#from ooiservices.app.uframe.deployment_tools import get_deployments_digest



def verify_cache(refresh=False):
    """ Verify necessary cached objects are available; if not get and set. Return asset_list data.
    """
    from ooiservices.app.uframe.status_tools import build_rds_cache
    verify_cache_required = False
    try:
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Ensure cached: 'vocab_dict' and 'vocab_codes'; 'stream_list'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        vocab_dict = get_vocab()
        stream_list = get_stream_list()
        asset_rds = get_asset_rds_cache()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Check 'asset_list', 'assets_dict', 'asset_rds'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not cache.get('asset_list') or not cache.get('assets_dict'): # or \
            #not cache.get('asset_rds'):
            verify_cache_required = True

        elif cache.get('asset_list') is None or cache.get('assets_dict') is None: # or \
            #cache.get('asset_rds') is None:
            verify_cache_required = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # If required, get asset(s) supporting cache(s)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verify_cache_required or refresh:
            data = get_assets_payload()
            if not data:
                message = 'No asset data returned from uframe.'
                current_app.logger.info(message)
                raise Exception(message)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate assets.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:
            data = cache.get('asset_list')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Populate reference designator digest information.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        verify_digests_required = False
        if not cache.get('rd_digests') or not cache.get('rd_digests_dict'):
            verify_digests_required = True

        if refresh or verify_digests_required:
            rd_digests = build_rds_cache()

        return data

    except Exception as err:
        message = 'Error getting uframe assets. %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get all assets from uframe.
def get_assets_payload():
    """ Get all assets from uframe, process and update caches for:
            'asset_list', 'assets_dict', 'asset_rds'
    """
    time = True
    try:
        print '\nCompiling assets...'
        try:
            # Clear all cache
            if cache.get('asset_list'):
                cache.delete('asset_list')
            if cache.get('assets_dict'):
                cache.delete('assets_dict')
        except Exception as err:
            message = str(err)
            raise Exception(message)

        # Get assets from uframe.
        result = get_assets_from_uframe()
        if not result:
            message = 'No uframe asset content returned.'
            raise Exception(message)

        # Get asset_list and asset_rds.
        data, asset_rds = new_compile_assets(result, compile_all=True)
        print '\n-- Completed loading assets....'
        if not data:
            message = 'Unable to process uframe assets; error creating assets_list.'
            raise Exception(message)
        if not asset_rds:
            message = 'Unable to process uframe assets; error creating asset_rds.'
            raise Exception(message)

        # Cache 'asset_list'.
        cache.set('asset_list', data, timeout=CACHE_TIMEOUT)
        check = cache.get('asset_list')
        if not check:
            message = 'Unable to process uframe assets; asset_list data is empty.'
            raise Exception(message)

        # Cache 'assets_dict'.
        assets_dict = populate_assets_dict(data)
        if assets_dict is None:
            message = 'Empty assets_dict returned from asset data.'
            raise Exception(message)

        print '\nCompleted compiling assets...\n'
        return data

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get assets_dict.
def populate_assets_dict(data):
    """ [Used by verify_cache.] Build and cache assets_dict from assets_list; on error log and return None.
    """
    try:
        # Using assets_list data, create assets_dict
        assets_dict = get_assets_dict_from_list(data)

        # If no assets_dict returned, log error
        if not assets_dict:
            message = 'Warning: empty assets_dict returned from get_assets_dict_from_list.'
            current_app.logger.info(message)

        # Verify assets_dict is type dict
        elif isinstance(assets_dict, dict):
            cache.set('assets_dict', assets_dict, timeout=CACHE_TIMEOUT)
        return assets_dict
    except Exception as err:
        message = 'Error populating \'assets_dict\'; %s' % str(err)
        current_app.logger.info(message)
        return None


def get_assets_dict_from_list(assets_list):
    """ From list of (ooi-ui-services versioned) list of assets, create assets dictionary by (key) id.
    """
    result = {}
    if assets_list:
        for item in assets_list:
            if 'id' in item:
                if item['id'] not in result:
                    result[item['id']] = item
    return result

# duplicated in asset_cache_tools
def _get_asset(id):
    """ Get an asset by asset uid.

    This function is used by routes:
        /uframe/assets/<int:id>
        /uframe/assets/uid/<string:uid>
    """
    asset = {}
    try:
        if id < 1:
            message = 'Invalid asset id value.'
            raise Exception(message)
        assets_dict = cache.get('assets_dict')
        if assets_dict is not None:
            if id in assets_dict:
                asset = assets_dict[id]
        else:
            data = uframe_get_asset_by_id(id)
            if data:
                data_list = [data]
                result, _ = new_compile_assets(data_list)
                if result:
                    asset = result[0]
        return asset
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset from uframe by asset uid.
def _get_ui_asset_by_uid(uid):
    """ Get asset from uframe by asset uid, return ui asset.
    """
    asset = {}
    try:
        data = uframe_get_asset_by_uid(uid)
        if data and data is not None:
            data_list = [data]
            result, _ = new_compile_assets(data_list)
            if result:
                asset = result[0]
        return asset
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Get asset from uframe by asset uid.
def get_uframe_asset_by_uid(uid):
    """ Get asset from uframe by asset uid, return ui asset.
    """
    try:
        data = uframe_get_asset_by_uid(uid)
        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def format_asset_for_ui(modified_asset):
    """ Format uframe asset into ui asset.
    """
    try:
        # Process remoteResources list.
        remoteResources = None
        if 'remoteResources' in modified_asset:
            remoteResources = modified_asset['remoteResources']
        if remoteResources is not None:
            modified_asset['remoteResources'] = post_process_remote_resources(remoteResources)

        # Prepare and convert asset.
        data_list = [modified_asset]
        try:
            asset_with_update, _ = new_compile_assets(data_list)
            updated_asset = asset_with_update[0]
        except Exception as err:
            message = 'Failed to format asset for display. %s' % str(err)
            raise Exception(message)
        if not updated_asset or updated_asset is None:
            raise Exception('Asset compilation failed to return a result.')
        return updated_asset
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Prepare remote resources for display.
def post_process_remote_resources(resources):
    """ Process resources list from uframe before returning for display (in UI).
    """
    try:
        if not resources:
            return resources
        for resource in resources:
            if '@class' in resource:
                del resource['@class']
        return resources
    except Exception as err:
        message = 'Error post-processing event for display. %s' % str(err)
        raise Exception(message)

'''
# todo - Refactor for new asset management data model; used by controller.py: get_svg_plot and dfs_streams
def get_events_by_ref_des(data, ref_des):
    """ Create the container for the processed response.
    """
    result = []

    # Get all the events to begin searching though...
    for row in data:
        # variables used in loop
        temp_dict = {}
        ref_des_check = ""
        try:

            if 'referenceDesignator' in row and row['referenceDesignator']['full']:
                ref_des_check = (row['referenceDesignator']['subsite'] + '-' + row['referenceDesignator']['node'] +
                                 '-' + row['referenceDesignator']['sensor'])
            else:
                if row['asset']['metaData']:
                    for metaData in row['asset']['metaData']:
                        if metaData['key'] == 'Ref Des':
                            ref_des_check = metaData['value']
            if ref_des_check == ref_des:
                temp_dict['ref_des'] = ref_des_check
                temp_dict['id'] = row['id']
                temp_dict['eventClass'] = row['eventClass']
                if row['eventClass'] == '.DeploymentEvent':
                    temp_dict['cruise_number'] = row['cruiseNumber']
                    temp_dict['cruise_plan_doc'] = row['cruisePlanDocument']
                    temp_dict['depth'] = row['depth']
                    temp_dict['lat_lon'] = row['locationLonLat']
                    temp_dict['deployment_number'] = row['deploymentNumber']
                temp_dict['tense'] = row['tense']
                start_date = num2date(float(row['startDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                temp_dict['start_date'] = start_date.strftime("%B %d %Y, %I:%M:%S %p")
                if row['endDate'] is not None:
                    end_date = num2date(float(row['endDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
                    temp_dict['end_date'] = end_date.strftime("%B %d %Y, %I:%M:%S %p")
                temp_dict['event_description'] = row['eventDescription']
                temp_dict['event_type'] = row['eventType']
                temp_dict['notes'] = row['notes']
                result.append(temp_dict)
                temp_dict = {}
        except (KeyError, TypeError):
            raise

    #result = jsonify({'events': result})
    return result
'''


def new_compile_assets(data, compile_all=False):
    """ Process list of asset dictionaries from uframe; transform into (ooi-ui-services) list of asset dictionaries.
    """
    test = True

    debug = False
    info = False                # Log missing vocab items when unable to create display name(s), etc. (default is True)
    new_data = []               # (assets) Mooring, Node and Sensor assets which have been deployed
    vocab_failures = []         # Vocabulary failures identified during asset processing are written to log.
    time = False
    base_asset_info ={
                'name': '',
                'type': '',
                'owner': '',
                'description': '',
                'longName': '',
                'array': '',
                'assembly': '',
                'asset_name': '',
                'mindepth': 0.0,
                'maxdepth': 0.0
            }
    try:
        if compile_all:
            time = True
            if time: print '\n-- Loading assets from uframe... '
            start = dt.datetime.now()
            if time: print '\t-- Start time: ', start
        update_asset_rds_cache = False
        dict_asset_ids = get_asset_rds_cache()
    except Exception as err:
        message = 'Error compiling asset_rds: %s' % err.message
        current_app.logger.info(message)
        raise Exception(message)

    # Valid processing types are those assetTypes which are subsequently mapped to reference designators.
    valid_asset_classes = get_asset_classes()
    valid_processing_types_uc = get_supported_asset_types()
    valid_processing_types = []
    for type in valid_processing_types_uc:
        valid_processing_types.append(type.lower())
    #asset_supported_types = get_supported_asset_types()
    #count = 0

    # Following import will be reviewed and refactored to proper location. (todo)
    from ooiservices.app.uframe.status_tools import get_last_deployment_digest
    for row in data:

        try:
            # Get asset_id, if not asset_id then continue
            asset_id = None
            if 'assetId' in row:
                row['id'] = row.pop('assetId')
                if not row['id'] or row['id'] is None:
                    print '\n Asset id value empty or null.'
                    continue
                asset_id = row['id']

            asset_uid = None
            if 'uid' in row:
                row['uid'] = row.pop('uid')
                asset_uid = row['uid']
            if asset_uid is None or not asset_uid or len(asset_uid) == 0:
                print '\t-- Note: Asset UID value empty or null; asset id: ', asset_id
                continue

            if 'events' in row:
                del row['events']
            if 'calibration' in row:
                del row['calibration']
            if 'remoteResources' in row:
                row['remoteResources'] = []
            #if len(row['remoteResources']) == 0:
            #    row['remoteResources'] = []
            row['asset_class'] = row.pop('@class')

            # Gather list of all assetType values RECEIVED (for information only)
            if row['assetType'] and row['assetType'] is not None:
                try:
                    asset_type = get_asset_type_display_name(row['assetType'])
                    row['assetType'] = asset_type
                except Exception as err:
                    message = 'get_uframe_asset_type: %s; error: %s' % (row['assetType'], str(err))
                    current_app.logger.info(message)
                    continue
            else:
                message = 'Asset (id: %d) has a null or empty assetType value.' % asset_id
                current_app.logger.info(message)
                continue

            # If ref_des not provided in row, try dictionary lookup.
            current_digest = None
            ref_des = None
            if 'ref_des' in row:
                if row['ref_des'] and row['ref_des'] is not None and len(row['ref_des']) != 0:
                    ref_des = row['ref_des']

            if ref_des is None:
                if asset_type in ['Platform', 'Node', 'Instrument']:
                    current_digest = get_last_deployment_digest(asset_uid)
                    if current_digest and current_digest is not None:
                        if asset_type == 'Platform':
                            ref_des = current_digest['subsite']
                        elif asset_type == 'Node':
                            ref_des = '-'.join([current_digest['subsite'], current_digest['node']])
                        elif asset_type == 'Instrument':
                            ref_des = '-'.join([current_digest['subsite'],
                                                current_digest['node'],
                                                current_digest['sensor']])

                        # If reference designator not available assets_rd, add.
                        if asset_id in dict_asset_ids:
                            if ref_des is not None:
                                if ref_des not in dict_asset_ids[asset_id]:
                                    dict_asset_ids[asset_id].append(ref_des)
                                    update_asset_rds_cache = True
                                    if test:
                                        print 'Notes: -- asset id/uid/type: %d/%s/%s  ref_des %s not in %s' % \
                                              (asset_id, asset_uid, asset_type, ref_des,dict_asset_ids[asset_id])


            # Populate manufactureInfo
            row['manufactureInfo'] = {}
            row['manufactureInfo']['manufacturer'] = row.pop('manufacturer')
            row['manufactureInfo']['modelNumber'] = row.pop('modelNumber')
            row['manufactureInfo']['serialNumber'] = row.pop('serialNumber')
            row['manufactureInfo']['firmwareVersion'] = row.pop('firmwareVersion')
            row['manufactureInfo']['softwareVersion'] = row.pop('softwareVersion')
            row['manufactureInfo']['shelfLifeExpirationDate'] = row.pop('shelfLifeExpirationDate')

            # Populate purchaseAndDeliveryInfo
            row['purchaseAndDeliveryInfo'] = {}
            if not row['deliveryDate'] or row['deliveryDate'] is None:
                row['purchaseAndDeliveryInfo']['deliveryDate'] = None
            else:
                row['purchaseAndDeliveryInfo']['deliveryDate'] = row.pop('deliveryDate')

            if not row['purchaseDate'] or row['purchaseDate'] is None:
                row['purchaseAndDeliveryInfo']['purchaseDate'] = None
            else:
                row['purchaseAndDeliveryInfo']['purchaseDate'] = row.pop('purchaseDate')
            row['purchaseAndDeliveryInfo']['purchasePrice'] = row.pop('purchasePrice')
            row['purchaseAndDeliveryInfo']['deliveryOrderNumber'] = row.pop('deliveryOrderNumber')

            # Populate partData
            row['partData'] = {}
            row['partData']['ooiPropertyNumber'] = row.pop('ooiPropertyNumber')
            row['partData']['ooiPartNumber'] = row.pop('ooiPartNumber')
            row['partData']['ooiSerialNumber'] = row.pop('ooiSerialNumber')
            row['partData']['institutionPropertyNumber'] = row.pop('institutionPropertyNumber')
            row['partData']['institutionPurchaseOrderNumber'] = row.pop('institutionPurchaseOrderNumber')

            # Populate physicalInfo dictionary. Move powerRequirements and depthRating into physicalInfo dictionary
            physicalInfo = {}
            physicalInfo['height'] = -1.0
            physicalInfo['weight'] = -1.0
            physicalInfo['width'] = -1.0
            physicalInfo['length'] = -1.0
            physicalInfo['depthRating'] = None
            physicalInfo['powerRequirements'] = None
            if 'physicalInfo' in row:
                if row['physicalInfo'] or row['physicalInfo'] is not None:
                    physicalInfo = row.pop('physicalInfo')
            if 'depthRating' in row:
                physicalInfo['depthRating'] = row.pop('depthRating')
            if 'powerRequirements' in row:
                physicalInfo['powerRequirements'] = row.pop('powerRequirements')
            row['physicalInfo'] = physicalInfo

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Get asset class based on reference designator
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if not row['asset_class'] or row['asset_class'] is None:
                message = 'asset_class empty or null for asset id %d.' % asset_id
                current_app.logger.info(message)
                continue

            # Validate asset_class, log asset class if unknown.
            asset_class = row.pop('asset_class')
            if asset_class not in valid_asset_classes:
                if info:
                    message = 'Asset class value (%s) not one of: %s' % (asset_class, valid_asset_classes)
                    current_app.logger.info(message)
                continue

            # Set default field values for assets without deployment/reference designators.
            row['deployment_number'] = ''
            row['deployment_numbers'] = []
            if 'lastModifiedTimestamp' in row:
                del row['lastModifiedTimestamp']

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Prepare assetInfo dictionary, populate with information or defaults.
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            row['assetInfo'] = deepcopy(base_asset_info)

            # Asset owner
            row['assetInfo']['owner'] = row.pop('owner')

            # Populate assetInfo 'type' with uframe provided assetType.
            row['assetInfo']['type'] = asset_type

            # Verify all necessary attributes are available, if not create and set to empty.
            if row['name']:
                row['assetInfo']['asset_name'] = row.pop('name')
            if row['description']:
                row['assetInfo']['description'] = row.pop('description')

            row['ref_des'] = None

            # Handle location information (if provided in asset, not required)
            latitude = None
            longitude = None
            depth = None
            orbitRadius = None
            """
            # Asset location is optional and not reflective of deployment information at this time.
            # Use data derived from asset/deployment/uid query instead until further notice.
            if 'location' in row and row['location'] is not None:
                    tmp = deepcopy(row['location'])
                    latitude, longitude, depth, orbitRadius, loc_list = get_location_fields(tmp)
            """

            if current_digest is not None:
                latitude = current_digest['latitude']
                longitude = current_digest['longitude']
                depth = current_digest['depth']
                orbitRadius = current_digest['orbitRadius']
            row['latitude'] = latitude
            row['longitude'] = longitude
            row['depth'] = depth
            row['orbitRadius'] = orbitRadius
            if 'location' in row:
                del row['location']

            #===========================================================================================
            if ref_des:
                # Set row values with reference designator
                row['ref_des'] = ref_des

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                # Populate assetInfo dictionary
                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                try:
                    # Get vocabulary dict for ref_des; contains name, long_name, mindepth, maxdepth, model, manufacturer
                    name = None
                    longName = None
                    mindepth = 0.0
                    maxdepth = 0.0
                    vocab_dict = get_vocab_dict_by_rd(ref_des)
                    if vocab_dict:
                        row['assetInfo']['mindepth'] = vocab_dict['mindepth']
                        row['assetInfo']['maxdepth'] = vocab_dict['maxdepth']
                        name = vocab_dict['name']
                        longName = vocab_dict['long_name']
                    else:
                        row['assetInfo']['mindepth'] = mindepth
                        row['assetInfo']['maxdepth'] = maxdepth

                    # Populate assetInfo - name, if failure to get display name, use ref_des, log failure.
                    if name is None:
                        if ref_des not in vocab_failures:
                            vocab_failures.append(ref_des)
                        if info:
                            message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                            current_app.logger.info(message)
                        name = ref_des
                    row['assetInfo']['name'] = name

                    # Populate assetInfo - long name, if failure to get long name then use ref_des, log failure.
                    if longName is None:
                        if ref_des not in vocab_failures:
                            vocab_failures.append(ref_des)
                        if info:
                            message = 'Vocab Note ----- reference designator (%s) failed to get display name for:' % ref_des
                            current_app.logger.info(message)
                        longName = ref_des
                    row['assetInfo']['longName'] = longName

                    # Populate assetInfo - array and assembly
                    if len(ref_des) >= 8:
                        if ref_des[:2] == 'RS':
                            row['assetInfo']['array'] = get_rs_array_name_by_rd(ref_des[:8])
                        else:
                            row['assetInfo']['array'] = get_display_name_by_rd(ref_des[:2])
                    if len(ref_des) >= 14:
                        row['assetInfo']['assembly'] = get_display_name_by_rd(ref_des[:14])
                    #=============================================================================
                except Exception as err:
                    # asset info error
                    message = 'asset (with rd) processing error: ' + str(err.message)
                    current_app.logger.info(message)
                    continue

            #===========================================================================================
            # Add new row to output dictionary
            if asset_id:
                new_data.append(row)
                # if new item for dictionary of asset ids, add id with value of reference designator
                if asset_id not in dict_asset_ids:
                    if ref_des:
                        if ref_des is not None:
                            dict_asset_ids[asset_id] = [ref_des]
                            update_asset_rds_cache = True
        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            continue
        # end of asset processing loop
        #- - - - - - - - - - - - - - -
        """
        count += 1
        if count >= 20:
            break
        """

    if compile_all:
        # Log vocabulary failures (occur when creating display names)
        if vocab_failures:
            vocab_failures.sort()
            message = 'These reference designator(s) are not defined, causing display name failures(%d): %s' \
                      % (len(vocab_failures), vocab_failures)
            current_app.logger.info(message)

        # Amend 'dict_asset_ids' to reflect information from processing
        if dict_asset_ids:
            if update_asset_rds_cache:
                asset_rds_cache_update(dict_asset_ids)
        print '\t-- Total number of assets compiled: ', len(new_data)

    if time:
        end = dt.datetime.now()
        if time: print '\t-- End time:   ', end
        if time: print '\t-- Time to load uframe assets: %s' % str(end - start)
    return new_data, dict_asset_ids


def _get_assets(use_min=False, sort=None, geoJSON=False):
    """
    """
    debug = True
    try:
        # Verify asset information available before continuing, if failure raise internal server error.
        try:
            data = verify_cache()
            if not data:
                message = 'Failed to get assets.'
                raise Exception(message)
        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            raise Exception(message)

        # Determine field to sort by, sort asset data (ooi-ui-services format. On bad field, raise exception.
        sort_by = ''
        try:
            if sort and sort is not None:
                sort_by = sort
            else:
                sort_by = 'ref_des'
            data = sorted(data, key=itemgetter(sort_by))
        except Exception as err:
            message = 'Unknown element to sort assets by \'%s\'. %s' % (sort_by, str(err))
            current_app.logger.info(message)
            raise Exception(message)

        # If using minimized ('min') or use_min, then strip asset data
        if use_min is True:
            for obj in data:
                if 'manufactureInfo' in obj:
                    del obj['manufactureInfo']
                if 'notes' in obj:
                    del obj['notes']
                if 'physicalInfo' in obj:
                    del obj['physicalInfo']
                if 'purchaseAndDeliveryInfo' in obj:
                    del obj['purchaseAndDeliveryInfo']
                if 'lastModifiedTimestamp' in obj:
                    del obj['lastModifiedTimestamp']
                if 'partData' in obj:
                    del obj['partData']
                if 'remoteResources' in obj:
                    del obj['remoteResources']

        #=================================================== To be deprecated
        # Replace with assets/nav routes.
        # Create toc information using geoJSON=true
        if geoJSON:
            #result = arrays_geojson()
            result = assets_query_geojson(data, status='block')
            if result and result is not None:
                data = result
        #====================================================================

        return data
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def assets_query_geojson(data, status='block'):
    """ Returns the geoJSON result currently being used by UI.
    """
    return_list = []
    unique = set()
    try:
        for obj in data:
            if obj['assetType'] == 'Array' or obj['assetType'] == 'Not Classified':
                continue
            if 'ref_des' in obj and obj['ref_des']:
                if obj['ref_des'] and obj['ref_des'] is not None:
                    if len(obj['ref_des']) <= 8 and 'latitude' in obj and 'longitude' in obj and 'depth' in obj:
                        if obj['ref_des'] not in unique:
                            unique.add(str(obj['ref_des']))
                            work = format_geojson_data(obj, status)    # todo - remove status here
                            if work is not None:
                                return_list.append(work)

        if not return_list or return_list is None:
            result = None
            try:
                result = sorted(return_list, key=itemgetter('reference_designator'))  # rd
            except Exception as err:
                print '\n errors: ', str(err)
                pass
            if result is None:
                return return_list
            return_list = result
        return return_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def format_geojson_data(obj, status='value'):
    try:
        work = {}
        latitude = None
        longitude = None
        depth = None
        mindepth = None
        maxdepth = None
        name = None
        uid = None
        reference_designator = obj['ref_des'][:]
        if 'latitude' in obj:
            latitude = obj['latitude']
            if latitude is not None:
                latitude = round(latitude, 4)
        if 'longitude' in obj:
            longitude = obj['longitude']
            if longitude is not None:
                longitude = round(longitude, 4)
        if 'depth' in obj:
            depth = obj['depth']
        if 'uid' in obj:
            uid = obj['uid']

        work['uid'] = uid
        work['reference_designator'] = reference_designator
        work['latitude'] = latitude
        work['longitude'] = longitude
        work['depth'] = depth
        """
        if 'assetInfo' in obj:
            #mindepth = 0
            if 'mindepth' in obj['assetInfo']:
                mindepth = obj['assetInfo']['mindepth']
            #maxdepth = 0
            if 'maxdepth' in obj['assetInfo']:
                maxdepth = obj['assetInfo']['maxdepth']
            if 'name' in obj['assetInfo']:
                name = obj['assetInfo']['name']
        """
        # Use vocab dict to populate mindepth and maxdepth
        vocab_dict = get_vocab_dict_by_rd(reference_designator)
        if vocab_dict and vocab_dict is not None:
            name = vocab_dict['name']
            mindepth = vocab_dict['mindepth']
            maxdepth = vocab_dict['maxdepth']
        else:
            print '\n No vocabulary dictionary - name, use reference designator: ', reference_designator
            name = reference_designator
            mindepth = 0.0
            maxdepth = 0.0
        work['display_name'] = name
        work['mindepth'] = mindepth
        work['maxdepth'] = maxdepth
        #================
        '''
        if not work:
            work = None
        else:
            work['status'] = get_status_data(reference_designator)
        return work
        '''
        if not work:
            work = None
        else:
            # work around for existing home page navigation.
            if latitude is None or longitude is None:
                """
                "geo_location": {
                    "coordinates": [
                      -1,
                      -1
                    ],
                    "depth": null
                  },
                """
                coordinates = [-1, -1]
            else:
                coordinates = [longitude, latitude]
            work['geo_location'] = {}
            work['geo_location']['coordinates'] = coordinates
            if depth is None:
                depth = 0
            work['geo_location']['depth'] = depth

        return work

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None

def arrays_geojson():
    """ Returns the geoJSON result currently being used by UI.

    {
        'array_id': asset['assetInfo']['refDes'][:2],
        'display_name': name,
        'geo_location': {
            'coordinates': coordinates,
            'depth': asset['assetInfo']['depth']
            },
        'mindepth': mindepth,
        'maxdepth': maxdepth,
        'reference_designator': asset['assetInfo']['refDes']
    }

    {
      "display_name": "Global Southern Ocean",
      "latitude": -54.0814,
      "longitude": -89.6652,
      "reference_designator": "GS",
      "status": {
        "legend": {
          "degraded": 0,
          "failed": 1,
          "notTracked": 0,
          "operational": 9,
          "removedFromService": 0
        },
        "total": 10
      }
    },
    """
    debug = True
    return_list = []
    from ooiservices.app.uframe.status_tools import get_status_arrays
    try:
        results = []
        result = get_status_arrays()
        if debug: print '\n debug -- result: ', result
        if result is not None:
            results = result
        else:
            return results

        # Format latitude, longitude, depth into geoJSON output.
        for array in results:
            if 'status' in array:
                del array['status']
            array['mindepth'] = 0.0
            array['maxdepth'] = 0.0
            latitude = None
            if 'latitude' in array:
                latitude = array.pop('latitude')
                if latitude is not None:
                    latitude = round(latitude, 4)
            longitude = None
            if 'longitude' in array:
                longitude = array.pop('longitude')
                if longitude is not None:
                    longitude = round(longitude, 4)
            depth = None
            if 'depth' in array:
                depth = array.pop('depth')
                if depth is not None:
                    depth = round(depth, 4)
            array['geo_location'] = {}
            if latitude is not None and longitude is not None:
                array['geo_location']['coordinates'] = [longitude, latitude]
            else:
                array['geo_location']['coordinates'] = [ -1, -1]
            array['geo_location']['depth'] = depth
        return results
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#=============================================
'''
def process_deployment_digests(uid, assetType):
    """
    For a list of deployment digests, get list of unique deployment numbers and rds.

    Sample digest:
        {
          "startTime" : 1437159840000,
          "depth" : 0.0,
          "subsite" : "CE01ISSP",
          "node" : "SP001",
          "sensor" : "00-SPPENG000",
          "deploymentNumber" : 3,
          "versionNumber" : 1,
          "eventId" : 23362,
          "editPhase" : "OPERATIONAL",
          "longitude" : -124.09567,
          "latitude" : 44.66415,
          "orbitRadius" : 0.0,
          "mooring_uid" : "N00262",
          "node_uid" : "N00123",
          "sensor_uid" : "R00102",
          "deployCruiseIdentifier" : null,
          "recoverCruiseIdentifier" : null,
          "waterDepth" : null,
          "endTime" : 1439424000000
        },
    """
    debug = False
    deployments = []
    rds = []
    reference_designator = None
    try:
        if not uid or uid is None or len(uid) == 0:
            message = 'Asset uid provided is null or empty; unable to process deployment digests for asset.'
            current_app.logger.info(message)
            return rds, deployments, reference_designator

        # Get deployments digests.
        results = get_deployments_digest(uid)
        if not results or results is None or len(results) <= 0:
            return [], [], None

        # Sort deployment digests.
        try:
            digests = sorted(results, key=itemgetter('deploymentNumber'), reverse=True)
        except:
            digests = results

        if digests:
            # Get reference designator for asset and deployment number it was associated with.
            reference_designator, deployment_number = get_digest_reference_designator(digests[0], assetType)

        # Sort digests in reverse order by deployment number.
        for digest in digests:
            if debug: print '\n debug -- digest[deploymentNumber]: ', digest['deploymentNumber']
            #print '\n debug -- digest: ', json.dumps(digest, indent=4, sort_keys=True)
            if 'deploymentNumber' in digest:
                if digest['deploymentNumber'] and digest['deploymentNumber'] is not None:
                    if digest['deploymentNumber'] not in deployments:
                        deployments.append(digest['deploymentNumber'])

            # Get reference designator (rd)
            rd = None
            subsite = None
            if 'subsite' in digest:
                subsite = digest['subsite']
            node = None
            if 'node' in digest:
                node = digest['node']
            sensor = None
            if 'sensor' in digest:
                sensor = digest['sensor']

            if assetType == 'Platform':
                if subsite and subsite is not None and len(subsite) > 0:
                    rd = subsite
            elif assetType == 'Node':
                if subsite and subsite is not None and len(subsite) > 0:
                    rd = subsite
                if node and node is not None and len(node) > 0:
                    rd = '-'.join([rd, node])
            elif assetType == 'Instrument':
                if subsite and subsite is not None and len(subsite) > 0:
                    rd = subsite
                    if node and node is not None and len(node) > 0:
                        rd = '-'.join([rd, node])
                        if sensor and sensor is not None and len(sensor) > 0:
                            rd = '-'.join([rd, sensor])
                        else:
                            rd = None
                    else:
                        rd = None
                else:
                    rd = None

            if debug: print '\n debug -- rd: ', rd
            if rd is not None:
                if rd not in rds:
                    rds.append(rd)

        return rds, deployments, reference_designator

    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_digest_reference_designator(digest, assetType):
    """

    """
    debug = True
    rd = None
    deployment_number = None
    try:
        if debug:
            print '\n debug -- Entered get_digest_reference_designator...'
            print '\n debug -- assetType: ', assetType
        if not digest or digest is None:
            return rd, deployment_number

        if 'deploymentNumber' in digest:
            deployment_number = digest['deploymentNumber']

        # Get reference designator (rd)
        rd = None
        subsite = None
        if 'subsite' in digest:
            subsite = digest['subsite']
        node = None
        if 'node' in digest:
            node = digest['node']
        sensor = None
        if 'sensor' in digest:
            sensor = digest['sensor']

        if assetType == 'Platform':
            if subsite and subsite is not None and len(subsite) > 0:
                rd = subsite
        elif assetType == 'Node':
            if subsite and subsite is not None and len(subsite) > 0:
                rd = subsite
            if node and node is not None and len(node) > 0:
                rd = '-'.join([rd, node])
        elif assetType == 'Instrument':
            if subsite and subsite is not None and len(subsite) > 0:
                rd = subsite
                if node and node is not None and len(node) > 0:
                    rd = '-'.join([rd, node])
                    if sensor and sensor is not None and len(sensor) > 0:
                        rd = '-'.join([rd, sensor])
                    else:
                        rd = None
                else:
                    rd = None
            else:
                rd = None
        if debug:
            print '\n debug -- deployment_number: ', deployment_number
            print '\n debug -- rd: ', rd
            print '\n debug -- Exit get_digest_reference_designator...'
        return rd, deployment_number
    except Exception as err:
        message = str(err)
        raise Exception(message)
'''