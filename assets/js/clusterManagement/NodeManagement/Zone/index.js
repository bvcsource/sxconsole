// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, Component } from 'react'
import { connect } from 'react-redux'

import { moveNode } from '../../actions'
import { getZoneNodeIds } from '../../reducers'
import Node from '../Node'
import { nodeDropTarget } from '../dnd'
import EmptyZone from './EmptyZone'
import ZoneHeading from './ZoneHeading'


const mapStateToProps = (state, ownProps) => ({
    nodeIds: getZoneNodeIds(state, ownProps.zoneName) || [],
})

@connect(mapStateToProps, { moveNode })
@nodeDropTarget
export default class Zone extends Component {
    static propTypes = {
        zoneName: PropTypes.string.isRequired,
        nodeIds: PropTypes.array.isRequired,
        moveNode: PropTypes.func.isRequired,
        connectDropTarget: PropTypes.func.isRequired,
    }

    render() {
        const zoneBody = this.props.connectDropTarget(
            <div className='row row-flex'>
                {this.renderNodes()}
            </div>
        )

        return (
            <div className='zones-management__zone'>
                <ZoneHeading zoneName={this.props.zoneName} />
                {zoneBody}
            </div>
        )
    }


    renderNodes() {
        if (this.props.nodeIds.length === 0) {
            return <EmptyZone />
        }
        return this.props.nodeIds.map(this.renderNode)
    }

    renderNode = id => (
        <Node
            key={id}
            nodeId={id}
            zoneName={this.props.zoneName}
        />
    )

}
