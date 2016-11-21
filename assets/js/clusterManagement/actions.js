// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import uuid from 'node-uuid'

import * as actionTypes from './actionTypes'

export const editNode = (id, payload) => ({
    type: actionTypes.EDIT_NODE,
    id,
    payload,
})

export const removeNode = id => ({
    type: actionTypes.REMOVE_NODE,
    id,
})

export const restoreNode = id => ({
    type: actionTypes.RESTORE_NODE,
    id,
})

export const addNode = payload => ({
    type: actionTypes.ADD_NODE,
    id: uuid.v4(),
    payload,
})

export const moveNode = (id, oldZone, newZone) => ({
    type: actionTypes.MOVE_NODE,
    id,
    oldZone,
    newZone,
})

export const markNodeAsFaulty = id => ({
    type: actionTypes.MARK_NODE_AS_FAULTY,
    id,
})

export const unmarkFaultyNode = id => ({
    type: actionTypes.UNMARK_FAULTY_NODE,
    id,
})

export const markNodeToReplace = (id, newPublicIp, newInternalIp) => ({
    type: actionTypes.MARK_NODE_TO_REPLACE,
    id,
    newPublicIp,
    newInternalIp,
})

export const cancelNodeReplacement = id => ({
    type: actionTypes.CANCEL_NODE_REPLACEMENT,
    id,
})

export const addZone = name => ({
    type: actionTypes.ADD_ZONE,
    name,
})

export const renameZone = (oldName, newName) => ({
    type: actionTypes.RENAME_ZONE,
    oldName,
    newName,
})

export const removeZone = name => ({
    type: actionTypes.REMOVE_ZONE,
    name,
})
