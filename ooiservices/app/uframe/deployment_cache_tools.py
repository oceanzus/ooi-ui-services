#!/usr/bin/env python

"""
Asset Management - Assets: Support for cache related functions.
"""
__author__ = 'Edna Donoughe'

from ooiservices.app import cache
from ooiservices.app.uframe.uframe_tools import _get_id_by_uid

CACHE_TIMEOUT = 172800


def refresh_deployment_cache(id, deployment, action):
    """ Perform deployment cache refresh.
    """
    try:
        deployment_cache_refresh(id, deployment, action)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def deployment_cache_refresh(id, deployment, action):
    """ Add an deployment to 'rd_assets' for deployment cache.
    {
        "assetUid" : null,
        "rd": "CE01ISSP-SP001-02-DOSTAJ000",
        "dataSource": "UI:user=edna",
        "deployCruiseInfo": null,
        "deployedBy": "Test engineer",
        "deploymentNumber": 3027,
        "editPhase" : "OPERATIONAL",
        "eventName": "Coastal Pioneer:Central Surface Piercing Profiler Mooring",
        "eventStartTime": 1506434340000,
        "eventStopTime": 1509034390000,
        "eventType": "DEPLOYMENT",
        "inductiveId" : null,
        "ingestInfo": null,
        "depth": 0.0,
        "longitude" : -124.09567,
        "latitude" : 44.66415,
        "orbitRadius": 0.0,
        "mooring_uid": "N00262",
        "node_uid": "N00122",
        "notes" : null,
        "recoverCruiseInfo": null,
        "recoveredBy": "Test engineer",
        "sensor_uid": "N00580",
        "tense": "UNKNOWN",
        "versionNumber": 3027
    }
    """
    debug = False
    try:
        if debug: print '\n debug -- Entered deployment_cache_refresh...action: ', action
        mooring_id, node_id, sensor_id, eventId, rd, deploymentNumber, location, startTime, stopTime = \
            get_deployment_cache_info(deployment)

        # Add deployment to deployment cache ('rd_assets')
        deployment_cache = cache.get('rd_assets')
        if deployment_cache:
            deployments_dict = deployment_cache
            if isinstance(deployments_dict, dict):

                # Determine if rd in deployments dictionary.
                if rd in deployments_dict:
                    work = deployments_dict[rd]

                    # If deployment number in dictionary, verify asset ids are represented.
                    if deploymentNumber in work:
                        #------------
                        # Update deployment asset ids with mooring, node and sensor id information
                        # Mooring
                        if debug: print '\n debug -- processing mooring_id...'
                        if mooring_id is not None:
                            target_asset_type = 'mooring'
                            if mooring_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(mooring_id)

                            if target_asset_type in work[deploymentNumber]['asset_ids_by_type']:
                                if mooring_id not in work[deploymentNumber]['asset_ids_by_type'][target_asset_type]:
                                    work[deploymentNumber]['asset_ids_by_type'][target_asset_type].append(mooring_id)
                            else:
                                work[deploymentNumber]['asset_ids_by_type'][target_asset_type] = [mooring_id]

                            # Main dictionary asset_ids list
                            if mooring_id not in work['asset_ids']:
                                work['asset_ids'].append(mooring_id)
                            if mooring_id not in work['asset_ids_by_type'][target_asset_type]:
                                work['asset_ids_by_type'][target_asset_type].append(mooring_id)

                        # Node
                        if debug: print '\n debug -- processing node_id...'
                        if node_id is not None:
                            target_asset_type = 'node'
                            if node_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(node_id)

                            if target_asset_type in work[deploymentNumber]['asset_ids_by_type']:
                                if node_id not in work[deploymentNumber]['asset_ids_by_type'][target_asset_type]:
                                    work[deploymentNumber]['asset_ids_by_type'][target_asset_type].append(node_id)
                            else:
                                work[deploymentNumber]['asset_ids_by_type'][target_asset_type] = [node_id]

                            # Main dictionary asset_ids list
                            if node_id not in work['asset_ids']:
                                work['asset_ids'].append(node_id)
                            if node_id not in work['asset_ids_by_type'][target_asset_type]:
                                work['asset_ids_by_type'][target_asset_type].append(node_id)

                        # Sensor
                        if debug: print '\n debug -- processing sensor_id...'
                        if sensor_id is not None:
                            target_asset_type = 'sensor'
                            if sensor_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(deploymentNumber)

                            if target_asset_type in work[deploymentNumber]['asset_ids_by_type']:
                                if sensor_id not in work[deploymentNumber]['asset_ids_by_type'][target_asset_type]:
                                    work[deploymentNumber]['asset_ids_by_type'][target_asset_type].append(sensor_id)
                            else:
                                work[deploymentNumber]['asset_ids_by_type'][target_asset_type] = [sensor_id]

                            # Main dictionary asset_ids list
                            if sensor_id not in work['asset_ids']:
                                work['asset_ids'].append(sensor_id)
                            if sensor_id not in work['asset_ids_by_type'][target_asset_type]:
                                work['asset_ids_by_type'][target_asset_type].append(sensor_id)

                        if debug: print '\n debug -- processing beginDT block...'
                        work[deploymentNumber]['beginDT'] = startTime
                        work[deploymentNumber]['endDT'] = stopTime
                        work[deploymentNumber]['eventId'] = eventId
                        work[deploymentNumber]['location'] = location
                        work[deploymentNumber]['tense'] = 'UNKNOWN'

                        # deploymentNumber in work, therefore should be in work[deployments, verify and update is not.
                        if deploymentNumber not in work['deployments']:
                            print '\n *** Added deploymentNumber %d for rd %s...' % (deploymentNumber, rd)
                            work['deployments'].append(deploymentNumber)
                        if work['deployments']:
                            work['deployments'].sort(reverse=True)
                            current_deployment_number = work['deployments'][0]

                        #------------

                            # Set all deployment cumulative tense values to 'PAST', then update current to 'PRESENT'
                            for number in work['deployments']:
                                work[number]['cumulative_tense'] = 'PAST'
                            work[current_deployment_number]['cumulative_tense'] = 'PRESENT'
                        else:
                            work['current_deployment'] = deploymentNumber
                            work[deploymentNumber]['cumulative_tense'] = 'PRESENT'

                    else:
                        new_deployment = {}
                        new_deployment['beginDT'] = startTime
                        new_deployment['endDT'] = stopTime
                        new_deployment['eventId'] = eventId
                        new_deployment['location'] = location
                        new_deployment['tense'] = 'UNKNOWN'
                        new_deployment['asset_ids_by_type'] = {'mooring': [], 'node': [], 'sensor': []}
                        new_deployment['asset_ids'] = []
                        work[deploymentNumber] = new_deployment
                        if mooring_id is not None:
                            if mooring_id not in work['asset_ids']:
                                work['asset_ids'].append(mooring_id)
                            if mooring_id not in work['asset_ids_by_type']['mooring']:
                                work['asset_ids_by_type']['mooring'].append(mooring_id)
                            if mooring_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(mooring_id)
                            if mooring_id not in work[deploymentNumber]['asset_ids_by_type']['mooring']:
                                work[deploymentNumber]['asset_ids_by_type']['mooring'].append(mooring_id)
                        if node_id is not None:
                            if node_id not in work['asset_ids']:
                                work['asset_ids'].append(node_id)
                            if node_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(node_id)
                            if node_id not in work['asset_ids_by_type']['node']:
                                work['asset_ids_by_type']['node'].append(node_id)
                            if node_id not in work[deploymentNumber]['asset_ids_by_type']['node']:
                                work[deploymentNumber]['asset_ids_by_type']['node'].append(node_id)
                        if sensor_id is not None:
                            if sensor_id not in work['asset_ids']:
                                work['asset_ids'].append(sensor_id)
                            if sensor_id not in work[deploymentNumber]['asset_ids']:
                                work[deploymentNumber]['asset_ids'].append(sensor_id)
                            if sensor_id not in work['asset_ids_by_type']['sensor']:
                                work['asset_ids_by_type']['sensor'].append(sensor_id)
                            if sensor_id not in work[deploymentNumber]['asset_ids_by_type']['sensor']:
                                work[deploymentNumber]['asset_ids_by_type']['sensor'].append(sensor_id)
                        if deploymentNumber not in work['deployments']:
                            work['deployments'].append(deploymentNumber)
                        deployments_list = work['deployments']
                        deployments_list.sort(reverse=True)
                        current_deployment_number = deployments_list[0]
                        work['current_deployment'] = current_deployment_number
                        # Set all deployment cumulative tense values to 'PAST', then update current to 'PRESENT'
                        for number in work['deployments']:
                            work[number]['cumulative_tense'] = 'PAST'
                        work[current_deployment_number]['cumulative_tense'] = 'PRESENT'
                    #---------

                # Build dictionary for rd, then add to rd_assets
                else:
                    if debug: print '\n debug -- Build dictionary for rd, then add to rd_assets...'
                    work = {}
                    work['current_deployment'] = deploymentNumber
                    work['deployments'] = [deploymentNumber]
                    work[deploymentNumber] = {}
                    work[deploymentNumber]['beginDT'] = startTime
                    work[deploymentNumber]['endDT'] = stopTime
                    work[deploymentNumber]['eventId'] = eventId
                    work[deploymentNumber]['location'] = location
                    work[deploymentNumber]['tense'] = 'UNKNOWN'
                    work[deploymentNumber]['current_deployment'] = deploymentNumber
                    work[deploymentNumber]['cumulative_tense'] = 'PRESENT'
                    work[deploymentNumber]['asset_ids_by_type'] = {'mooring': [], 'node': [], 'sensor': []}
                    work[deploymentNumber]['asset_ids'] = []
                    work['asset_ids'] = []
                    work['asset_ids_by_type'] = {'mooring': [], 'node': [], 'sensor': []}
                    if mooring_id is not None:
                        work['asset_ids'].append(mooring_id)
                        work['asset_ids_by_type']['mooring'].append(mooring_id)
                        work[deploymentNumber]['asset_ids'].append(mooring_id)
                        work[deploymentNumber]['asset_ids_by_type']['mooring'].append(mooring_id)
                    if node_id is not None:
                        if node_id not in work['asset_ids']:
                            work['asset_ids'].append(node_id)
                        if node_id not in work[deploymentNumber]['asset_ids']:
                            work[deploymentNumber]['asset_ids'].append(node_id)
                        work['asset_ids_by_type']['node'].append(node_id)
                        work[deploymentNumber]['asset_ids_by_type']['node'].append(node_id)
                    if sensor_id is not None:
                        if sensor_id not in work['asset_ids']:
                            work['asset_ids'].append(sensor_id)
                        if sensor_id not in work[deploymentNumber]['asset_ids']:
                            work[deploymentNumber]['asset_ids'].append(sensor_id)
                        work['asset_ids_by_type']['sensor'].append(sensor_id)
                        work[deploymentNumber]['asset_ids_by_type']['sensor'].append(sensor_id)

                    deployments_dict[rd] = work

                cache.set('rd_assets', deployments_dict, timeout=CACHE_TIMEOUT)

        return
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_deployment_cache_info(deployment):
    """ Get bundle of information used to update deployment cache.
    """
    try:
        startTime = None
        stopTime = None

        #- - - - - - - - - - - - - - - - - - - -
        # Get deployment event id.
        #- - - - - - - - - - - - - - - - - - - -
        if 'eventId' not in deployment:
            message = 'The event id was not provided in deployment for cache refresh.'
            raise Exception(message)
        else:
            eventId = deployment['eventId']
        if eventId is None:
            message = 'The event id is null, invalid deployment for cache refresh.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - -
        # Get deployment reference designator.
        #- - - - - - - - - - - - - - - - - - - -
        if 'rd' not in deployment:
            message = 'The reference designator was not provided in deployment for cache refresh.'
            raise Exception(message)
        else:
            rd = deployment['rd']
        if rd is None:
            message = 'The reference designator is null, invalid deployment for cache refresh.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - -
        # Get deploymentNumber.
        #- - - - - - - - - - - - - - - - - - - -
        if 'deploymentNumber' not in deployment:
            message = 'The deployment number was not provided in deployment for cache refresh.'
            raise Exception(message)
        else:
            deploymentNumber = deployment['deploymentNumber']
        if deploymentNumber is None:
            message = 'The deployment number is null, invalid deployment for cache refresh.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - -
        # Get location, startTime, stopTime.
        #- - - - - - - - - - - - - - - - - - - -
        location = get_location_dictionary(deployment)
        if 'startTime' in deployment:
            startTime = deployment['startTime']
        if 'stopTime' in deployment:
            stopTime = deployment['stopTime']

        #- - - - - - - - - - - - - - - - - - - -
        # Get asset ids by type.
        #- - - - - - - - - - - - - - - - - - - -
        mooring_id = None
        node_id = None
        sensor_id = None
        # Get mooring_id using mooring_uid.
        if 'mooring_uid' in deployment:
            if not deployment['mooring_uid']:
                deployment['mooring_uid'] = None
            target_asset_type = 'Mooring'
            if deployment['mooring_uid'] is not None:
                mooring_id, asset_type = _get_id_by_uid(deployment['mooring_uid'])
                if asset_type != target_asset_type:
                    message = 'The asset with uid \'%s\', asset id %d is a %s asset, not a \'%s\'.' % \
                              (deployment['mooring_uid'], mooring_id, asset_type, target_asset_type)
                    raise Exception(message)

        # Get node_id using node_uid.
        if 'node_uid' in deployment:
            if not deployment['node_uid']:
                deployment['node_uid'] = None
            target_asset_type = 'Node'
            if deployment['node_uid'] is not None:
                node_id, asset_type = _get_id_by_uid(deployment['node_uid'])
                if node_id is None:
                    message = 'The node_uid \'%s\' is invalid, it failed to return an asset id from uframe.' % \
                              deployment['mooring_uid']
                    raise Exception(message)
                if asset_type != target_asset_type:
                    message = 'The asset with uid \'%s\', asset id %d is a %s asset, not a \'%s\'.' % \
                              (deployment['node_uid'], node_id, asset_type, target_asset_type)
                    raise Exception(message)

        # Get sensor_id using sensor_uid.
        if 'sensor_uid' in deployment:
            if not deployment['sensor_uid']:
                deployment['sensor_uid'] = None
            target_asset_type = 'Sensor'
            if deployment['sensor_uid'] is not None:
                sensor_id, asset_type = _get_id_by_uid(deployment['sensor_uid'])
                if sensor_id is None:
                    message = 'The sensor_id \'%s\' is invalid, it failed to return an asset id from uframe.' % \
                              deployment['sensor_uid']
                    raise Exception(message)
                if asset_type != target_asset_type:
                    message = 'The asset with uid \'%s\', asset id %d is a %s asset, not a \'%s\'.' % \
                              (deployment['sensor_uid'], sensor_id, asset_type, target_asset_type)
                    raise Exception(message)

        return mooring_id, node_id, sensor_id, eventId, rd, deploymentNumber, location, startTime, stopTime
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_location_dictionary(deployment):
    """ Construct location dictionary from ui deployment information.
    """
    try:
        have_location_dict = False
        latitude = None
        longitude = None
        location = None
        depth = None
        orbitRadius = None
        if 'depth' in deployment:
            depth = deployment['depth']
            if depth is None:
                depth = 0.0
            else:
                have_location_dict = True
        if 'orbitRadius' in deployment:
            orbitRadius = deployment['orbitRadius']
            if orbitRadius is None:
                orbitRadius = 0.0
            else:
                have_location_dict = True
        if 'latitude' in deployment:
            latitude = deployment['latitude']
        if 'longitude' in deployment:
            longitude = deployment['longitude']
        if latitude is not None and longitude is not None:
            location = [longitude, latitude]
            have_location_dict = True
        else:
            if latitude is None:
                latitude = 0.0
            if longitude is None:
                longitude = 0.0
        if have_location_dict:
            location_dict = {}
            location_dict['latitude'] = latitude
            location_dict['longitude'] = longitude
            location_dict['location'] = location
            location_dict['depth'] = depth
            location_dict['orbitRadius'] = orbitRadius
        else:
            location_dict = None
        return location_dict

    except Exception as err:
        message = str(err)
        raise Exception(message)