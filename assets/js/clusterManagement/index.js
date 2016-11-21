// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import React from 'react'
import { render } from 'react-dom'
import { createStore } from 'redux'
import { Provider } from 'react-redux'

import mainReducer from './reducers'
import NodeManagement from './NodeManagement'
import MarkFaulty from './MarkFaulty'
import ReplaceFaulty from './ReplaceFaulty'
import Warnings from './Warnings'


const initData = $('#nodes-init').data('init')

const nodes = initData.nodeIds.map(id => initData.nodesById[id])

const store = createStore(
    mainReducer, {
        zones: {
            byName: initData.zoneNodes,
            pristineByName: initData.zoneNodes,
        },
        nodes: {
            ids: initData.nodeIds,
            byId: initData.nodesById,
            pristineById: initData.nodesById,
        },
    }
)

render(
    <Warnings nodes={nodes} />,
    document.getElementById('warnings'))

render(
    <Provider store={store}>
        <NodeManagement />
    </Provider>,
    document.getElementById('nodes'))

render(
    <Provider store={store}>
        <MarkFaulty />
    </Provider>,
    document.getElementById('mark-faulty'))

render(
    <Provider store={store}>
        <ReplaceFaulty />
    </Provider>,
    document.getElementById('replace-faulty'))
