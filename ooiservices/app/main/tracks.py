#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'James Case'

from flask import jsonify, request
from ooiservices.app.main import api
from ooiservices.app import db
from authentication import auth
from ooiservices.app.models import Track
from ooiservices.app.decorators import scope_required
import json
from wtforms import ValidationError

@api.route('/track', methods=['GET'])
def get_tracks():
    if 'asset_id' in request.args:
        tracks = Track.query.filter_by(asset_id=request.args['asset_id']).all()
    else:
        tracks = Track.query.all()
    return jsonify({ 'tracks' : [track.to_json() for track in tracks] })

@api.route('/track/<int:id>', methods=['GET'])
def get_track(id):
    track = Track.query.get(id)
    if track is None:
        return jsonify(error="Track Not Found"), 404
    return jsonify(**track.to_json())

@auth.login_required
@api.route('/track', methods=['POST'])
def post_track():
    try:
        data = json.loads(request.data)
        new_track = Track.from_json(data)
        db.session.add(new_track)
        db.session.commit()
    except ValidationError as e:
        return jsonify(error=e.message), 400
    return jsonify(**new_track.to_json()), 201

@auth.login_required
@api.route('/track/<int:id>', methods=['PUT'])
def put_track(id):
    try:
        data = json.loads(request.data)
        existingTrack = Track.query.get(id)
        if existingTrack is None:
            return jsonify(error="Invalid ID, record not found"), 404
        existingTrack.asset_id = data.get('asset_id', existingTrack.asset_id)
        existingTrack.track_start = data.get('track_start', existingTrack.track_start)
        existingTrack.track_end = data.get('track_end', existingTrack.track_end)
        existingTrack.geo_location = data.get('geo_location', existingTrack.geo_location)
        db.session.add(existingTrack)
        db.session.commit()
    except ValidationError as e:
        return jsonify(error=e.message), 400
    return jsonify(**existingTrack.to_json()), 200

@api.route('/track/<int:id>', methods=['DELETE'])
@auth.login_required
@scope_required('user_admin')
def delete_track(id):
    track = Track.query.get(id)
    if track is None:
        return jsonify(error="Track Not Found"), 404
    db.session.delete(track)
    db.session.commit()
    return jsonify(), 200
