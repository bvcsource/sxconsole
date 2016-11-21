// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { getZoneNodeIds } from '../reducers'
import Node from './Node'
import ZoneHeading from '../components/ZoneHeading'


const mapStateToProps = (state, ownProps) => ({
    nodeIds: getZoneNodeIds(state, ownProps.zoneName) || [],
})

@connect(mapStateToProps)
export default class Zone extends PureComponent {
    static propTypes = {
        zoneName: PropTypes.string.isRequired,
        nodeIds: PropTypes.array.isRequired,
    }

    render() {
        return (
            <div className='zones-management__zone'>
                <ZoneHeading zoneName={this.props.zoneName} />
                <div
                    className='row row-flex'
                    children={this.props.nodeIds.map(this.renderNode)}
                />
            </div>
        )
    }

    renderNode = id => <Node key={id} nodeId={id} />
}
