#!/usr/bin/env python
"""
Specific testing for events routes

Routes:
[GET] /events/<int:id>                          # Get event. This should not be used by UI; if needed, then discuss!
[GET] /events/types                             # Get all supported event types
[GET] /events/uid/<string:uid>                  # Get all events of all types for asset with uid
      /events/uid/<string:uid>?type=EventType   # Get all events for asset with uid, only type(s) identified
      # Example: /uframe/events/uid/A00228?type=ATVENDOR
      # Example: /uframe/events/uid/A00228?type=ATVENDOR,INTEGRATION

[POST] /events                                  # Create an event of each eventType.
[PUT]  /events/<int:id>                         # Update events of each eventType.

"""
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import (url_for)
from ooiservices.app import (create_app, db)
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.uframe.common_tools import get_event_types
from ooiservices.app.uframe.event_tools import (get_rd_by_asset_id)    # get_uframe_event (future test)
from ooiservices.app.uframe.deployment_tools import (is_instrument, is_platform, is_mooring)
from unittest import skipIf
import os
import requests

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class EventsTestCase(unittest.TestCase):

    # enable verbose (during development and documentation) to get a list of
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    debug = False
    root = 'http://localhost:4000'

    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_username = 'admin'
        test_password = 'test'
        Organization.insert_org()

        User.insert_user(username=test_username, password=test_password)

        self.client = self.app.test_client(use_cookies=False)
        UserScope.insert_scopes()
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='redmine').first()     # added
        admin.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='asset_manager').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test cases
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_events(self):
        """
        Exercise event routes:
        [GET]    /events/types           # Get all supported event types
        [GET]    /events/uid/<string:uid # Get events for asset with uid
        [GET]    /assets/<int:id>/events # Get all events for asset with asset id.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Get some assets
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))
        if verbose: print '\n -- len(assets): ', len(assets)

        # Verify there asset objects which are dictionaries
        asset = assets[0]
        self.assertTrue(asset is not None)
        self.assertTrue(asset)
        self.assertTrue(isinstance(asset, dict))

        # Get asset_id
        self.assertTrue('id' in asset)
        asset_id = asset['id']
        self.assertTrue(asset_id is not None)
        self.assertTrue(asset_id)

        # Get asset uid
        self.assertTrue('uid' in asset)
        asset_uid = asset['uid']
        self.assertTrue(asset_uid is not None)
        self.assertTrue(asset_uid)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types (list)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_event_type')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        event_types = results['event_types']
        self.assertTrue(event_types is not None)
        self.assertTrue(isinstance(event_types, list))
        if debug: print '\n -- len(event_types): ', len(event_types)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events by asset uid
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_events_by_uid', uid=asset_uid)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Get events by bad asset uid #(returns empty dict if asset not found, status code 200)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_events_by_uid', uid='notgood')
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 400)
        result = json.loads(response.data)
        self.assertTrue(result is not None)
        self.assertTrue(result)
        result = None

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Get events for asset (by event_id)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('uframe.get_asset_events', id=asset_id)
        if verbose: print '\n ----- url: ', url
        response = self.client.get(url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset(%d): %s' % (asset_id, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue('events' in result)
        self.assertTrue(isinstance(result['events'], dict))
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, dict))
        self.assertTrue(len(events_by_type) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) Process event types by type, validate fields
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose: print '\n -- len(result): ', len(result)
        event_types = get_event_types()
        for event_type in events_by_type:
            if debug: print '\n debug -- Event_type: ', event_type
            self.assertTrue(event_type in event_types)
            self.assertTrue(event_type in events_by_type)
            self.assertTrue(isinstance(events_by_type[event_type], list))
            event_ids = []
            if events_by_type[event_type]:
                if debug: print '\n Have events of %s event type.' % event_type
                events = events_by_type[event_type]
                for event in events:
                    self.assertTrue(event is not None)
                    self.assertTrue(isinstance(event, dict))
                    #if debug: print '\n ****** event: ', event
                    self.assertTrue('eventId' in event)
                    self.assertTrue(event['eventId'])
                    if event['eventId'] not in event_ids:
                        event_ids.append(event['eventId'])

                """
                # If events, get events in event_ids list from uframe.
                if event_ids:
                    if debug: print '\n ****** Have %s event_ids(%d): %s' % (event_type, len(event_ids), event_ids)
                    for id in event_ids:
                        result = get_uframe_event(id)

                        if debug: print '\n -- fetched event(%d): %s' % (id, result)
                        self.assertTrue(result is not None)
                        self.assertTrue(result)
                        self.assertTrue(isinstance(result, dict))
                        self.assertTrue(len(result) > 0)
                        try:
                            validate_required_fields_are_provided_uframe(event_type, result, 'update')
                        except Exception as err:
                            message = str(err)
                            if verbose: print '\n test exception: ', message
                            continue
                    if debug: print '\n Done processing event_ids for %s events.' % event_type
                """

    def test_create_event_types_random(self):
        """
        Create events of different types for three random assets with an asset type of mooring, platform and sensor.

        Following event types not support and why:
        'DEPLOYMENT'           # (general)
        'CALIBRATION_DATA'     # create and update api not available
        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_event_types()

        # Remove event_type which are not supported at this time.
        event_types.remove('DEPLOYMENT')
        event_types.remove('CALIBRATION_DATA')
        if 'RECOVERY' in event_types:
            event_types.remove('RECOVERY')

        # For now remove cruise info until I have a way to generate next unique cruise id.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')

        if verbose: print '\n event_types: ', event_types

        #========================================================================
        # Get three assets, one for mooring, node and sensor; generate variety of event types for each.
        #========================================================================
        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        have_mooring_id = False
        have_platform_id = False
        have_instrument_id = False

        mooring_id = None
        platform_id = None
        instrument_id = None

        mooring_uid = None
        platform_uid = None
        instrument_uid = None

        mooring_rd = None
        platform_rd = None
        instrument_rd = None

        from random import randint
        count = 0
        while not have_mooring_id or not have_platform_id or not have_instrument_id and count <= number_of_assets:

            count +=1
            asset_index = randint(0, (number_of_assets-1))
            #print '\n Random asset_index: %d' % asset_index

            # Select an asset...
            asset = assets[asset_index]
            self.assertTrue(asset is not None)
            self.assertTrue(asset)
            self.assertTrue(isinstance(asset, dict))

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            if is_mooring(rd):
                if not have_mooring_id:
                    have_mooring_id = True
                    mooring_id = asset_id
                    mooring_uid = asset_uid
                    mooring_rd = rd

            elif is_platform(rd):
                if not have_platform_id:
                    have_platform_id = True
                    platform_id = asset_id
                    platform_uid = asset_uid
                    platform_rd = rd

            elif is_instrument(rd):
                if not have_instrument_id:
                    have_instrument_id = True
                    instrument_id = asset_id
                    instrument_uid = asset_uid
                    instrument_rd = rd
        if verbose:
            print '\n Note: Number of loops to get three items of interest: %d ' % count
            print '\n ----- Mooring:'
            print '\n\t mooring_id: %d' % mooring_id
            print '\n\t mooring_uid: %s' % mooring_uid
            print '\n\t mooring_rd: %s' % mooring_rd
            print '\n ----- Platform:'
            print '\n\t platform_id: %d' % platform_id
            print '\n\t platform_uid: %s' % platform_uid
            print '\n\t platform_rd: %s' % platform_rd
            print '\n ----- Instrument:'
            print '\n\t instrument_id: %d' % instrument_id
            print '\n\t instrument_uid: %s' % instrument_uid
            print '\n\t instrument_rd: %s' % instrument_rd

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to a mooring asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_types = ['INTEGRATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for mooring - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                mooring_id, mooring_uid, mooring_rd)

            # How many of this type of event does mooring currently have?
            events_before = self.get_events_for_an_event_type(event_type, mooring_uid)
            number_before = len(events_before)
            if verbose: print '\n Number before creating %s event: %d' % (event_type, number_before)

            # Create another
            uid, input = self.create_event_data(event_type, mooring_uid, mooring_rd)
            self._create_event_type(event_type, uid, input)

            # How many total now?
            events_after = self.get_events_for_an_event_type(event_type, mooring_uid)
            number_after = len(events_after)
            if verbose: print ' Number after creating %s event: %d' % (event_type, number_after)
            self.assertTrue((number_after - number_before), 1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to a platform asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_types = ['INTEGRATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for platform - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                                platform_id, platform_uid, platform_rd)
            # How many of this type of event does mooring currently have?
            events_before = self.get_events_for_an_event_type(event_type, platform_uid)
            number_before = len(events_before)
            if verbose: print '\n Number before creating %s event: %d' % (event_type, number_before)

            # Create another
            uid, input = self.create_event_data(event_type, platform_uid, platform_rd)
            self._create_event_type(event_type, uid, input)

            # How many total now?
            events_after = self.get_events_for_an_event_type(event_type, platform_uid)
            number_after = len(events_after)
            if verbose: print ' Number after creating %s event: %d' % (event_type, number_after)
            self.assertTrue((number_after - number_before), 1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add event(s) to an instrument asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event_types = ['INTEGRATION']
        for event_type in event_types:
            if verbose: print '\n Creating %s event for instrument - asset id/uid/rd: %d/%s/%s' % (event_type,
                                                                        instrument_id, instrument_uid, instrument_rd)

            # How many of this type of event does mooring currently have?
            events_before = self.get_events_for_an_event_type(event_type, instrument_uid)
            number_before = len(events_before)
            if verbose: print '\n Number before creating %s event: %d' % (event_type, number_before)

            # Create another
            uid, input = self.create_event_data(event_type, instrument_uid, instrument_rd)
            self._create_event_type(event_type, uid, input)

            # How many total now?
            events_after = self.get_events_for_an_event_type(event_type, instrument_uid)
            number_after = len(events_after)
            if verbose: print ' Number after creating %s event: %d' % (event_type, number_after)
            self.assertTrue((number_after - number_before), 1)

    def test_create_event_types_numerous_regular(self):
        """
        Create events of different types for numerous assets, configure for more than two assets.
        This test case is useful for populating large quantities of event (all types) on a uframe server. Careful.

        Following event types not support and why:
        'DEPLOYMENT'           # (general)
        'CALIBRATION_DATA'     # create and update api not available
        'RECOVERY'             # OBE?

        Routes:
        [GET]   /assets
        [GET]   /events/uid/<string:uid>
        [GET]   /events/uid/<string:uid>?type=EventType   # Example: /uframe/events/uid/A00228?type=ACQUISITION
        [PUT]   /events/<int:id>
        [POST]  /events
        """
        debug = self.debug
        verbose = self.verbose
        event_types = get_event_types()

        # Remove event_type which are not supported at this time.
        event_types.remove('DEPLOYMENT')
        event_types.remove('CALIBRATION_DATA')
        if 'RECOVERY' in event_types:
            event_types.remove('RECOVERY')

        # For now remove cruise info until determine a way to generate next unique cruise id.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')

        if verbose: print '\n event_types: ', event_types

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        count = 0
        maximum_count = 1
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...
            asset = assets[count]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            asset_type = ''
            if is_mooring(rd):
                asset_type = 'mooring'
            elif is_platform(rd):
                asset_type = 'platform'
            elif is_instrument(rd):
                asset_type = 'instrument'

            message = '\n (%d) Processing %s asset...' % ((count + 1), asset_type)
            if verbose: print '\n %s' % message
            count +=1

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Add event(s) to asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Note: To test single event type, set event_types list here: event_types = ['UNSPECIFIED']
            #event_types = ['INTEGRATION']  # ['ACQUISITION'] #
            for event_type in event_types:
                if verbose: print '\n Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                """
                # Note: Add in if running small quantities of assets or to see event counts before and after create.
                # How many of this type of event does mooring currently have?
                events_before = self.get_events_for_an_event_type(event_type, asset_uid)
                number_before = len(events_before)
                if verbose: print '\t Number before creating %s event: %d' % (event_type, number_before)
                """

                # Create an event
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                event_id, last_modified = self._create_event_type(event_type, uid, input)
                if verbose: print '\n Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                """
                # Note: Add in if running small quantities of assets or to see event counts before and after create.
                # How many events now?
                events_after = self.get_events_for_an_event_type(event_type, asset_uid)
                number_after = len(events_after)
                if verbose: print '\t Number after creating %s event: %d' % (event_type, number_after)
                self.assertTrue((number_after - number_before), 1)
                """

                if verbose:
                    print '\n***********************************************************************'
                    print '\n Now performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                update_event_id = self._update_event_type(event_type, uid, input, event_id)
                if verbose: print '\n Updated eventId: %d ' % update_event_id
                self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count

    def test_create_event_types_numerous_requests(self):
        """
        Create events of different types for numerous assets, configure for more than two assets.
        This test case is useful for populating large quantities of event (all types) on a uframe server. Careful.

        Following event types not support and why:
        'DEPLOYMENT'           # (general)
        'CALIBRATION_DATA'     # create and update api not available
        'RECOVERY'             # OBE?

        Routes:
        [GET]   /assets
        [GET]   /events/uid/<string:uid>
        [GET]   /events/uid/<string:uid>?type=EventType   # Example: /uframe/events/uid/A00228?type=ACQUISITION
        [PUT]   /events/<int:id>
        [POST]  /events
        """
        verbose = self.verbose
        event_types = get_event_types()

        # Remove event_type which are not supported at this time.
        event_types.remove('DEPLOYMENT')
        event_types.remove('CALIBRATION_DATA')
        if 'RECOVERY' in event_types:
            event_types.remove('RECOVERY')

        # For now remove cruise info until determine a way to generate next unique cruise id.
        if 'CRUISE_INFO' in event_types:
            event_types.remove('CRUISE_INFO')
        if verbose: print '\n event_types: ', event_types

        # Get some assets...
        assets = self.get_some_assets()
        self.assertTrue(assets is not None)
        self.assertTrue(assets)
        self.assertTrue(isinstance(assets, list))

        number_of_assets = len(assets)
        if verbose: print '\n Have some assets (%d)' % number_of_assets

        count = 0
        maximum_count = 1
         #number_of_assets
        while count <= number_of_assets and count < maximum_count:

            # Select an asset...
            asset = assets[count]

            # Get asset_id, asset_uid, rd.
            asset_id, asset_uid, rd = self.get_id_uid_rd(asset)
            asset_type = ''
            if is_mooring(rd):
                asset_type = 'mooring'
            elif is_platform(rd):
                asset_type = 'platform'
            elif is_instrument(rd):
                asset_type = 'instrument'

            message = '\n (%d) Processing %s asset...' % ((count + 1), asset_type)
            if verbose: print '\n %s' % message
            count +=1

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Add event(s) to asset.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Note: To test single event type, set event_types list here:
            #event_types = ['STORAGE']
            for event_type in event_types:
                if verbose: print '\n Creating %s event - asset id/uid/rd: %d/%s/%s' % (event_type, asset_id, asset_uid, rd)

                """
                # Note: Add in if running small quantities of assets or to see event counts before and after create.
                # How many of this type of event does mooring currently have?
                events_before = self.get_events_for_an_event_type(event_type, asset_uid)
                number_before = len(events_before)
                if verbose: print '\t Number before creating %s event: %d' % (event_type, number_before)
                """

                # Create another
                uid, input = self.create_event_data(event_type, asset_uid, rd)
                event_id, last_modified = self._create_event_type_requests(event_type, uid, input)
                if verbose: print '\n (requests) Created eventId: %d and lastModifiedTimestamp: %d' % (event_id, last_modified)

                """
                # Note: Add in if running small quantities of assets or to see event counts before and after create.
                # How many events now?
                events_after = self.get_events_for_an_event_type(event_type, asset_uid)
                number_after = len(events_after)
                if verbose: print '\t Number after creating %s event: %d' % (event_type, number_after)
                self.assertTrue((number_after - number_before), 1)
                """

                if verbose:
                    print '\n***********************************************************************'
                    print '\n Now performing an UPDATE on event we just created...'
                # Update the one we just created
                uid, input = self.update_event_data(event_type, asset_uid, rd, event_id, last_modified)
                update_event_id = self._update_event_type_requests(event_type, uid, input, event_id)
                if verbose: print '\n (requests) Updated eventId: %d ' % update_event_id
                self.assertTrue(event_id, update_event_id)

        if verbose: print '\n Note: Number of assets processed: %d ' % count

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_id_uid_rd(self, asset):
        """ For an asset, get id, uid and rd.
        """
        debug = False
        try:
            # Get asset_id
            self.assertTrue('id' in asset)
            asset_id = asset['id']
            self.assertTrue(asset_id is not None)
            self.assertTrue(asset_id)
            if debug: print '\n Have asset_id: %d' % asset_id

            # Get asset uid
            self.assertTrue('uid' in asset)
            asset_uid = asset['uid']
            self.assertTrue(asset_uid is not None)
            self.assertTrue(asset_uid)
            if debug: print '\n Have asset_uid: %s ' % asset_uid

            # Get reference designator
            rd = get_rd_by_asset_id(asset_id)
            if debug: print '\n Have rd: %s ' % rd

            return asset_id, asset_uid, rd

        except Exception:
            print '\n exception getting asset id, uid and rd.'
            return None, None, None

    def get_events_for_an_event_type(self, event_type, uid):
        verbose = False
        headers = self.get_api_headers('admin', 'test')
        base_url = url_for('uframe.get_events_by_uid', uid=uid)
        target_url = base_url + '?type=' + event_type
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if verbose: print '\n -- fetched asset uid %s %s events: %s' % (uid, event_type, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][event_type]
        if verbose: print '\n Number of %s events returned: %d' % (event_type, len(some_events))

        return some_events

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type(self, _event_type, uid, input):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Define variables specific to event type
        if debug: print '\n Creating new event of type %s' % _event_type
        target_event_type = _event_type
        key = target_event_type

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_url = url_for('uframe.get_event_type')
        response = self.client.get(test_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get asset with uid 'A00391.1'; get asset_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset_by_uid', uid=uid), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset (%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get events for asset with uid 'A00391.1'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_events_by_uid', uid=uid)
        if verbose: print '\n Base url: ', base_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid events(%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)

        # Get events by type dictionary, key is event_type
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(len(events_by_type) > 0)

        # Create list of event_types returned for this asset
        event_types = events_by_type.keys()
        self.assertTrue(len(event_types) > 0)
        if debug: print '\n Have event_types: ', event_types

        # Get all uframe supported event types
        all_event_types = get_event_types()
        self.assertTrue(isinstance(all_event_types, list))
        self.assertTrue(len(all_event_types) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Determine number of events of target event type currently available
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        target_events = []
        target_event_ids = []
        if target_event_type in event_types:
            target_events = events_by_type[target_event_type]
            if target_events:
                for event in target_events:
                    if 'event_id' in event:
                        if event['event_id']:
                            if event['event_id'] not in target_event_ids:
                                target_event_ids.append(event['event_id'])

        if debug: print '\n Number of %s events: %d' % (target_event_type, len(target_events))
        number_of_target_events = len(target_events)

        # Verify number of events by query (using type=target_event_type)
        target_url = base_url + '?type=' + key
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][key]
        if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
        self.assertEquals(len(some_events), number_of_target_events)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test create (line 668) CREATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.create_event')
        if debug: print '\n create url: ', url
        goo = json.dumps(input)
        response = self.client.post(url, headers=headers, data=goo)
        if debug:
            print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            print '\n response_data: ', response_error

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
        #print '\n event_id: ', event_id
        self.assertTrue('lastModifiedTimestamp' in event)
        last_modified = event['lastModifiedTimestamp']
        self.assertTrue(last_modified is not None)
        #print '\n last_modified: ', last_modified

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify number of events has increased by one
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        target_url = base_url + '?type=' + key
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][key]
        if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
        self.assertEquals(len(some_events), number_of_target_events + 1)

        return event_id, last_modified



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Create event_type using requests
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _create_event_type_requests(self, _event_type, uid, input):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        # Define variables specific to event type
        if verbose: print '\n Creating new event of type %s' % _event_type
        target_event_type = _event_type
        key = target_event_type

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Positive) GET event types
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_url = url_for('uframe.get_event_type')
        response = self.client.get(test_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        results = json.loads(response.data)
        self.assertTrue('event_types' in results)
        if debug: print '\n -- len(results): ', len(results)
        self.assertTrue(results is not None)
        self.assertTrue(isinstance(results, dict))

        # Verify there are event_types in a list
        events_by_type = results['event_types']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(isinstance(events_by_type, list))
        if debug: print '\n -- len(events_by_type): ', len(events_by_type)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get asset with uid 'A00391.1'; get asset_id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('uframe.get_asset_by_uid', uid=uid), headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset (%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue(isinstance(result, dict))

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get events for asset with uid 'A00391.1'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        base_url = url_for('uframe.get_events_by_uid', uid=uid)
        if verbose: print '\n Base url: ', base_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid events(%s): %s' % (uid, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)

        # Get events by type dictionary, key is event_type
        events_by_type = result['events']
        self.assertTrue(events_by_type is not None)
        self.assertTrue(len(events_by_type) > 0)

        # Create list of event_types returned for this asset
        event_types = events_by_type.keys()
        self.assertTrue(len(event_types) > 0)
        if debug: print '\n Have event_types: ', event_types

        # Get all uframe supported event types
        all_event_types = get_event_types()
        self.assertTrue(isinstance(all_event_types, list))
        self.assertTrue(len(all_event_types) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Determine number of events of target event type currently available
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        target_events = []
        target_event_ids = []
        if target_event_type in event_types:
            target_events = events_by_type[target_event_type]
            if target_events:
                for event in target_events:
                    if 'event_id' in event:
                        if event['event_id']:
                            if event['event_id'] not in target_event_ids:
                                target_event_ids.append(event['event_id'])

        if debug: print '\n Number of %s events: %d' % (target_event_type, len(target_events))
        number_of_target_events = len(target_events)

        # Verify number of events by query (using type=target_event_type)
        target_url = base_url + '?type=' + key
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][key]
        if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
        self.assertEquals(len(some_events), number_of_target_events)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug:
            print '\n Create %s event' % key
            print '\n debug ********\n test create (line 668) CREATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))
        url = self.root
        url += url_for('uframe.create_event')
        if debug: print '\n debug -- Requests Create url: ', url
        data = json.dumps(input)
        timeout = 5
        timeout_read = 30
        response_data = None
        #response = requests.post(url, timeout=(timeout, timeout_read), headers=self.request_headers(), data=data)
        response = requests.post(url, timeout=(timeout, timeout_read),  data=data)
        if debug: print '\n debug -- Test: Create response.status_code: ', response.status_code
        if response.status_code != 200:
            if debug: print '\n Failed to execute to localhost:4000 create event, status_code: ', response.status_code
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Failed Event create data from POST: %s' % response_data
        else:
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Test: Successful Event create data from POST (json.loads(response.content)): %s' % response_data

        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
        #print '\n event_id: ', event_id
        self.assertTrue('lastModifiedTimestamp' in event)
        last_modified = event['lastModifiedTimestamp']
        self.assertTrue(last_modified is not None)
        #print '\n last_modified: ', last_modified

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Verify number of events has increased by one
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        target_url = base_url + '?type=' + key
        if verbose: print '\n target_url: ', target_url
        response = self.client.get(base_url, headers=headers)
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)
        #if debug: print '\n -- fetched asset uid %s %s events: %s' % (uid, key, result)
        self.assertTrue(result is not None)
        self.assertTrue('events' in result)
        self.assertTrue(result['events'] is not None)
        some_events = result['events'][key]
        if debug: print '\n Number of %s events returned: %d' % (key, len(some_events))
        self.assertEquals(len(some_events), number_of_target_events + 1)
        return event_id, last_modified


    def request_headers(self):
        """ Headers for uframe PUT and POST. """
        return {"Content-Type": "application/json"}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update event_type - regular
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _update_event_type(self, _event_type, uid, input, event_id):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n **** Update %s event' % _event_type
            print '\n **** Update event_id: %r' % event_id
            print '\n **** Update input: %r' % input

        if debug:
            print '\n debug ********\n test update (line 756) UPDATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = url_for('uframe.update_event', id=event_id)
        if verbose: print '\n **** Update url: ', url
        goo = json.dumps(input)
        response = self.client.put(url, headers=headers, data=goo)
        if response.status_code != 200:
            print '\n response.status_code: ', response.status_code
            response_error = json.loads(response.data)
            print '\n response_error: ', response_error

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.data is not None)
        response_data = json.loads(response.data)
        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
        return event_id


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Update event_type - using requests
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _update_event_type_requests(self, _event_type, uid, input, event_id):
        """
        Create event.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Update Event
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if verbose:
            print '\n **** Update %s event' % _event_type
            print '\n **** Update event_id: %r' % event_id
            print '\n **** Update input: %r' % input

        if debug:
            print '\n debug ********\n test update (line 756) UPDATE request_data(%d): %r' % (len(input),
                                                              json.dumps(input, indent=4, sort_keys=True))

        url = self.root
        url += url_for('uframe.update_event', id=event_id)
        if debug: print '\n debug -- Requests Update url: ', url

        data = json.dumps(input)
        timeout = 5
        timeout_read = 30
        response_data = None
        response = requests.put(url, timeout=(timeout, timeout_read), headers=self.request_headers(), data=data)
        if debug: print '\n debug -- Test: Update response.status_code: ', response.status_code
        if response.status_code != 200:
            if debug: print '\n Failed to execute to localhost:4000 update event, status_code: ', response.status_code
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Failed Event update data from POST: %s' % response_data
        else:
            if response.content:
                response_data = json.loads(response.content)
                if debug: print '\n Successful Event update data from POST: %s' % response_data

        self.assertTrue('event' in response_data)
        event = response_data['event']
        self.assertTrue(event is not None)
        self.assertTrue('eventId' in event)
        event_id = event['eventId']
        self.assertTrue(event_id is not None)
        return event_id


    def get_some_assets(self):
        """
        Get assets to assist in testing events.
        """
        debug = self.debug
        verbose = self.verbose
        headers = self.get_api_headers('admin', 'test')
        try:
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # (Positive) GET assets
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            url = url_for('uframe.get_assets')
            if verbose: print '\n ----- url: ', url
            response = self.client.get(url, headers=headers)
            self.assertEquals(response.status_code, 200)
            results = json.loads(response.data)
            self.assertTrue('assets' in results)
            if debug: print '\n -- len(results): ', len(results)
            self.assertTrue(results is not None)
            self.assertTrue(isinstance(results, dict))

            # Verify there are asset objects in a list
            assets = results['assets']
            self.assertTrue(assets is not None)
            self.assertTrue(isinstance(assets, list))
            if debug: print '\n -- len(assets): ', len(assets)

            return assets

        except Exception as err:
            if verbose: print '\n exception: ', str(err)
            return None

    # Data used to create different event types.
    def create_event_data(self, event_type, uid, rd):
        input = {}
        notes = 'Create new %s event for %s, (assetUid: %s)' % (event_type, rd, uid)
        if event_type == 'ACQUISITION':
            input = {
                      'purchasePrice': None,
                      'purchaseDate': None,
                      'deliveryDate': None,
                      'purchasedBy': None,
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': None,
                      'eventType': 'ACQUISITION',
                      'eventName': rd,
                      'eventStartTime': None,
                      'eventStopTime': None,
                      'notes': notes,
                      'tense': 'UNKNOWN',
                      'dataSource': None,
                      'assetUid': uid
                      }

        elif event_type == 'ASSET_STATUS':
            input = {
                    'severity': 5,
                    'reason': None,
                    'location': None,
                    'status': None,
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'ATVENDOR':
            input = {
                    'reason': 'Broken during storm at sea.',
                    'authorizationNumber': None,
                    'vendorIdentification': None,
                    'authorizationForPayment': None,
                    'invoiceNumber': None,
                    'vendorPointOfContact': None,
                    'sentToVendorBy': None,
                    'receivedFromVendorBy' : None,
                    'eventType': 'ATVENDOR',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'CRUISE_INFO':
            input = {
                    'uniqueCruiseIdentifer': 'CE-2016-0102',
                    'cruiseIdentifier': 'Test CE Cruise Info 2016',
                    'shipName': 'M/V Gallant',
                    'eventType': 'CRUISE_INFO',
                    'eventStartTime': 1453308000000,
                    'eventStopTime': 1453508700000,
                    'notes': notes,
                    'eventName': 'Test CE Cruise Info 2016',
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'INTEGRATION':
            input = {
                    'integrationInto': None,
                    'deploymentNumber': 3,
                    'versionNumber': 1,
                    'integratedBy': 'Engineer, RPS ASA',
                    'eventType': 'INTEGRATION',
                    'eventName':  rd,
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'LOCATION':
            input = {
                    'depth': 551.27,
                    'longitude': -70.77599,
                    'latitude': 40.36341,
                    'orbitRadius': 0.0,
                    'eventType': 'LOCATION',
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'RETIREMENT':
            input = {
                    'reason': 'All done with this.',
                    'disposition': 'Unknown',
                    'retiredBy': 'Engineer at RPS ASA',
                    'eventType': 'RETIREMENT',
                    'eventStartTime': 1398039070000,
                    'eventStopTime': 1405382400000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid
                    }

        elif event_type == 'STORAGE':
            input = {
                    'buildingName': 'Tower',
                    'eventName': rd,
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'eventType': 'STORAGE',
                    'notes': notes,
                    'performedBy': 'Engineer, RPS ASA',
                    'physicalLocation': 'Narragansett, RI',
                    'roomIdentification': '23',
                    'shelfIdentification': 'Cube 7-27',
                    'dataSource': None,
                    'tense': None,
                    'assetUid': uid
                    }

        elif event_type == 'UNSPECIFIED':
            input = {
                    'dataSource': None,
                    'eventName': rd,
                    'eventStartTime': 1398039060000,
                    'eventStopTime': 1405382400000,
                    'eventType': 'UNSPECIFIED',
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'assetUid': uid
                    }

        string_input = self.get_event_input_as_string(input)
        return uid, string_input

    # Data used to update different event types.
    def update_event_data(self, event_type, uid, rd, event_id, last_modified):
        #print '\n debug -- update_event_data -- event_type: ', event_type
        input = {}
        notes = 'Update new %s event for %s, associated with asset: %s)' % (event_type, rd, uid)
        if event_type == 'ACQUISITION':
            input = {
                      'purchasePrice': None,
                      'purchaseDate': 1398040000000,
                      'deliveryDate': 1398050000000,
                      'purchasedBy': None,
                      'vendorIdentification': None,
                      'vendorPointOfContact': None,
                      'receivedFromVendorBy': None,
                      'authorizationNumber': None,
                      'authorizationForPayment': None,
                      'invoiceNumber': None,
                      'eventType': 'ACQUISITION',
                      'eventName': rd,
                      'eventStartTime': 1398060000000,
                      'eventStopTime':  1398070000000,
                      'notes': notes,
                      'tense': 'UNKNOWN',
                      'dataSource': None,
                      'assetUid': uid,
                      'eventId': event_id,
                      'lastModifiedTimestamp': last_modified
                      }

        elif event_type == 'ASSET_STATUS':
            input = {
                    'severity': 4,
                    'reason': 'At operational capability; check battery power again in 5 days.',
                    'location': 'Onsite',
                    'status': 'Operational',
                    'eventType': 'ASSET_STATUS',
                    'eventStartTime': 1398039160000,
                    'eventStopTime': 1405382410000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'ATVENDOR':

            notes = 'The are serious concerns about some newer components used to '
            notes += 'refurbish the hardware. Issues configuring to OEM specs '
            notes += 'during calibration. Please review.'

            input = {
                    'reason': 'Dial not working properly do to power issues.',
                    'authorizationNumber': '10147',
                    'vendorIdentification': 'vendor A',
                    'authorizationForPayment': None,
                    'invoiceNumber': '2016-45870',
                    'vendorPointOfContact': 'Vendor Technician',
                    'sentToVendorBy': 'Raytheon Engineer',
                    'receivedFromVendorBy': 'Marine technician',
                    'eventType': 'ATVENDOR',
                    'eventStartTime': 1398039160000,
                    'eventStopTime': 1405382430000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'CRUISE_INFO':
            input = {
                    'uniqueCruiseIdentifer': 'CE-2016-0102',
                    'cruiseIdentifier': 'Test CE Cruise Info 2016',
                    'shipName': 'M/V Gallant',
                    'eventType': 'CRUISE_INFO',
                    'eventStartTime': 1453309000000,
                    'eventStopTime': 1453508710000,
                    'notes': notes,
                    'eventName': 'Test CE Cruise Info 2016',
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'INTEGRATION':
            integrationInto = {
                                'node': 'RID26',
                                'subsite': 'CP01CNSM',
                                'sensor': '04-VELPTA000'
                              }
            input = {
                    'integrationInto': None,
                    'deploymentNumber': 1,
                    'versionNumber': 2,
                    'integratedBy': 'Engineer 2, RPS ASA',
                    'eventType': 'INTEGRATION',
                    'eventName':  rd,
                    'eventStartTime': 1398039260000,
                    'eventStopTime': 1405382420000,
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                      'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'LOCATION':
            input = {
                    'depth': 551.27,
                    'longitude': -70.8125,
                    'latitude': 40.467731,
                    'orbitRadius': 0.0,
                    'eventType': 'LOCATION',
                    'eventStartTime': 1398039360000,
                    'eventStopTime': 1405382430000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'RETIREMENT':
            input = {
                    'reason': 'Equipment beyond repair.',
                    'disposition': 'Disposed',
                    'retiredBy': 'Engineer at RPS ASA',
                    'eventType': 'RETIREMENT',
                    'eventStartTime': 1398039570000,
                    'eventStopTime': 1405382450000,
                    'notes': notes,
                    'eventName': rd,
                    'tense': 'UNKNOWN',
                    'dataSource': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'STORAGE':
            input = {
                    'buildingName': 'Marine Storage',
                    'eventName': rd,
                    'eventStartTime': 1398039660000,
                    'eventStopTime': 1405382460000,
                    'eventType': 'STORAGE',
                    'notes': notes,
                    'performedBy': 'Engineer, RPS ASA',
                    'physicalLocation': 'URI, Narragansett, RI',
                    'roomIdentification': '55-104',
                    'shelfIdentification': '4139-03',
                    'dataSource': None,
                    'tense': None,
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        elif event_type == 'UNSPECIFIED':
            input = {
                    'dataSource': None,
                    'eventName': rd,
                    'eventStartTime': 1398039860000,
                    'eventStopTime': 1405382480000,
                    'eventType': 'UNSPECIFIED',
                    'notes': notes,
                    'tense': 'UNKNOWN',
                    'assetUid': uid,
                    'eventId': event_id,
                    'lastModifiedTimestamp': last_modified
                    }

        #string_input = self.get_event_input_as_string(input)
        string_input = self.get_event_input_as_unicode(input)
        #print '\n debug -- Completed get update string event.'
        return uid, string_input

    def get_event_input_as_string(self, data):
        """ Take input from UI and present all values as string type. Leaves nulls.
        Handles one dict level down. Used to simulate UI data from jgrid submit.
        """
        debug = False
        try:
            if debug: print '\n debug -- get_event_input_as_string'
            string_data = data.copy()
            keys = data.keys()
            for key in keys:
                if data[key] is not None:
                    if not isinstance(data[key], dict):
                        string_data[key] = str(data[key])
                    else:
                        if debug: print '\n Field is dict: ', key
                        tmp_dict = data[key].copy()
                        for k,v in tmp_dict.iteritems():
                            if v is not None:
                                if not isinstance(v, dict):
                                    string_data[key][k] = str(v)
            return string_data

        except Exception as err:
            if debug: print '\n exception: ', str(err)
            raise

    def get_event_input_as_unicode(self, data):
        """ Take input from UI and present all values as string type. Leaves nulls.
        Handles one dict level down. Used to simulate UI data from jgrid submit.
        """
        debug = False
        try:
            if debug: print '\n debug -- get_event_input_as_unicode'
            string_data = data.copy()
            keys = data.keys()
            for key in keys:
                if data[key] is not None:
                    if not isinstance(data[key], dict):
                        string_data[key] = unicode(data[key])
                    else:
                        if debug: print '\n Field is dict: ', key
                        tmp_dict = data[key].copy()
                        for k,v in tmp_dict.iteritems():
                            if v is not None:
                                if not isinstance(v, dict):
                                    string_data[key][k] = unicode(v)
            return string_data

        except Exception as err:
            if debug: print '\n exception: ', str(err)
            raise