// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import sortBy from 'lodash/sortBy'
import omit from 'lodash/omit'
import difference from 'lodash/difference'
import { combineReducers } from 'redux'
import { ADD_NODE, RENAME_ZONE, REMOVE_ZONE, ADD_ZONE, MOVE_NODE } from '../actionTypes'


export default combineReducers({ byName, pristineByName })

function byName(state={}, action) {
    switch (action.type) {
    case ADD_NODE:
        return {
            ...state,
            '': zoneNodeIds(state[''], action),
        }
    case MOVE_NODE: {
        return {
            ...state,
            [action.oldZone]: difference(state[action.oldZone], [action.id]),
            [action.newZone]: [...state[action.newZone], action.id],
        }
    }
    case RENAME_ZONE: {
        return {
            ...omit(state, action.oldName),
            [action.newName]: state[action.oldName],
        }
    }
    case REMOVE_ZONE: {
        return {
            ...omit(state, action.name),
            '': [...state[''], ...state[action.name]],
        }
    }
    case ADD_ZONE: {
        return {
            ...state,
            [action.name]: [],
        }
    }
    default:
        return state
    }
}

function zoneNodeIds(state=[], action) {
    switch (action.type) {
    case ADD_NODE:
        return [
            ...state,
            action.id,
        ]
    default:
        return state
    }
}

function pristineByName(state={}) {
    return state
}

export const getZonesMap = state => state.byName
export const getPristineZonesMap = state => state.pristineByName
export const getZoneNames = state => sortBy(
    Object.keys(getZonesMap(state)),
    name => [name === '', name]
)
export const getZoneNodeIds = (state, name) => getZonesMap(state)[name]
