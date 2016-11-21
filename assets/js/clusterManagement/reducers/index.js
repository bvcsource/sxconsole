// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import { combineReducers } from 'redux'

import nodes, * as fromNodes from './nodes'
import zones, * as fromZones from './zones'


export default combineReducers({ nodes, zones })

export const getNodeIds = state => fromNodes.getNodeIds(state.nodes)
export const getNode = (state, id) => fromNodes.getNode(state.nodes, id)
export const getPristineNode = (state, id) => fromNodes.getPristineNode(state.nodes, id)
export const getRemainingNodes = state => fromNodes.getRemainingNodes(state.nodes)
export const getNodesMarkedAsFaulty = state => fromNodes.getNodesMarkedAsFaulty(state.nodes)
export const getNodesMarkedForReplacement = state => (
    fromNodes.getNodesMarkedForReplacement(state.nodes)
)

export const getZonesMap = state => fromZones.getZonesMap(state.zones)
export const getPristineZonesMap = state => fromZones.getPristineZonesMap(state.zones)
export const getZoneNames = state => fromZones.getZoneNames(state.zones)
export const getZoneNodeIds = (state, name) => fromZones.getZoneNodeIds(state.zones, name)
