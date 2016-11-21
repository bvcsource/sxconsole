// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import map from 'lodash/map'
import omit from 'lodash/omit'
import mapValues from 'lodash/mapValues'
import isEqual from 'lodash/isEqual'
import isMatch from 'lodash/isMatch'
import intersection from 'lodash/intersection'
import { PropTypes } from 'react'
import { connect } from 'react-redux'

import BaseCommandModal from '../BaseCommandModal'
import { getRemainingNodes, getPristineNode, getZonesMap, getPristineZonesMap } from '../reducers'


function mapStateToProps(state) {
    const nodes = getRemainingNodes(state)

    const remainingNodeIds = map(nodes, 'uuid')
    const pickRemainingNodeIds = nodeIds => intersection(
        nodeIds,
        remainingNodeIds
    )
    const validZones = omit(
        getZonesMap(state),
        ''
    )
    const zones = mapValues(
        validZones,
        pickRemainingNodeIds
    )

    const areZonesPristine = () => isEqual(
        zones,
        getPristineZonesMap(state)
    )
    const areNodesPristine = () => nodes.every(
        node => isMatch(
            node,
            getPristineNode(state, node.uuid)
        )
    )
    const isPristine = areZonesPristine() && areNodesPristine()

    return { nodes, zones, isPristine }
}


@connect(mapStateToProps)
export default class SubmitChangesModal extends BaseCommandModal {
    static propTypes = {
        nodes: PropTypes.array.isRequired,
        zones: PropTypes.object.isRequired,
        isPristine: PropTypes.bool.isRequired,
    }
    urlName = 'modifyCluster'
    modalTitle = __("Submit changes?")
    triggerText = __("Submit changes")
    submitText = __("Submit")
    triggerClassName = 'btn btn-primary'

    getFormData = () => ({
        nodes: this.props.nodes,
        zones: this.props.zones,
    })

    isTriggerDisabled = () => (
        this.props.isPristine ||
            (this.props.nodes.length === 0)
    )
}
