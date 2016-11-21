// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import pick from 'lodash/pick'
import { combineReducers } from 'redux'

import * as actionTypes from '../actionTypes'


export default combineReducers({ ids, byId, pristineById })

function ids(state=[], action) {
    switch (action.type) {
    case actionTypes.ADD_NODE:
        return [
            ...state,
            action.id,
        ]
    default:
        return state
    }
}

function byId(state={}, action) {
    switch (action.type) {
    case actionTypes.EDIT_NODE:
    case actionTypes.REMOVE_NODE:
    case actionTypes.RESTORE_NODE:
    case actionTypes.ADD_NODE:
    case actionTypes.MARK_NODE_AS_FAULTY:
    case actionTypes.UNMARK_FAULTY_NODE:
    case actionTypes.MARK_NODE_TO_REPLACE:
    case actionTypes.CANCEL_NODE_REPLACEMENT:
        return {
            ...state,
            [action.id]: node(state[action.id], action),
        }
    default:
        return state
    }
}

function pristineById(state={}) {
    return state
}

function node(state, action) {
    switch (action.type) {
    case actionTypes.EDIT_NODE:
        const newData = pick(
            action.payload,
            ['capacity', 'publicIp', 'privateIp']
        )
        return {
            ...state,
            ...newData,
        }
    case actionTypes.REMOVE_NODE:
        return {
            ...state,
            isRemoved: true,
        }
    case actionTypes.RESTORE_NODE:
        return {
            ...state,
            isRemoved: false,
        }
    case actionTypes.ADD_NODE:
        const nodeData = pick(
            action.payload,
            ['capacity', 'publicIp', 'privateIp', 'uuid']
        )
        return {
            ...nodeData,
            uuid: action.id,
            isNew: true,
        }
    case actionTypes.MARK_NODE_AS_FAULTY:
        return {
            ...state,
            markedAsFaulty: true,
        }
    case actionTypes.UNMARK_FAULTY_NODE:
        return {
            ...state,
            markedAsFaulty: false,
        }
    case actionTypes.MARK_NODE_TO_REPLACE:
        return {
            ...state,
            newPublicIp: action.newPublicIp,
            newInternalIp: action.newInternalIp,
            markedForReplacement: true,
        }
    case actionTypes.CANCEL_NODE_REPLACEMENT:
        return {
            ...state,
            newPublicIp: undefined,
            newInternalIp: undefined,
            markedForReplacement: false,
        }
    default:
        return state
    }
}

export const getNodeIds = state => state.ids
export const getNode = (state, id) => state.byId[id]
export const getAllNodes = state => (
    getNodeIds(state)
        .map(id => getNode(state, id))
)
export const getPristineNode = (state, id) => state.pristineById[id]
export const getRemainingNodes = state => (
    getAllNodes(state)
        .filter(n => !n.isRemoved)
)
export const getNodesMarkedAsFaulty = state => (
    getAllNodes(state)
        .filter(n => n.markedAsFaulty)
)
export const getNodesMarkedForReplacement = state => (
    getAllNodes(state)
        .filter(n => n.markedForReplacement)
)
