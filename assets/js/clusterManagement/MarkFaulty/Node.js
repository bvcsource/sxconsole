// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { getNode, getPristineNode } from '../reducers'
import NodeInfoModal from '../NodeInfoModal'
import NodeComponent from '../components/Node'
import MarkNodeAsFaultyButton from './MarkNodeAsFaultyButton'
import UnmarkFaultyNodeButton from './UnmarkFaultyNodeButton'


const mapStateToProps = (state, ownProps) => ({
    node: getNode(state, ownProps.nodeId),
    pristineNode: getPristineNode(state, ownProps.nodeId),
})

@connect(mapStateToProps)
export default class Node extends PureComponent {
    static propTypes = {
        nodeId: PropTypes.string.isRequired,
        node: PropTypes.object.isRequired,
    }

    render() {
        return (
            <div className='col-xs-6 col-md-6 col-lg-4'>
                <div>
                    <NodeComponent classModifiers={this.getNodeModifiers()}>
                        {this.renderNodeButtons()}
                        {this.renderNodeInfo()}
                    </NodeComponent>
                </div>
            </div>
        )
    }

    renderNodeInfo() {
        const { node } = this.props
        return (
            <div>
                <div className='bold' children={node.publicIp} />
                <div>
                    {this.displayNodeStatus()}
                    {', '}
                    {bytes(node.capacity)}
                </div>
            </div>
        )
    }

    renderNodeButtons() {
        const { node, nodeId } = this.props
        const disabled = this.isFaulty()
        return (
            <div style={{ float: 'right' }}>
                <NodeInfoModal
                    node={node}
                    triggerClassName={'btn btn-default btn-xs'}
                    triggerDisabled={false}
                />
                {' '}
                {this.markedAsFaulty()
                    ? <UnmarkFaultyNodeButton nodeId={nodeId} disabled={disabled} />
                    : <MarkNodeAsFaultyButton nodeId={nodeId} disabled={disabled} />
                }
            </div>
        )
    }

    displayNodeStatus() {
        if (this.isFaulty()) {
            return __("Faulty")
        }
        if (this.markedAsFaulty()) {
            return __("Marked as faulty")
        }
        return __("Healthy")
    }

    isFaulty = () => this.props.node.isFaulty
    markedAsFaulty = () => this.isFaulty() || this.props.node.markedAsFaulty

    getNodeModifiers() {
        const modifiers = []
        if (this.isFaulty()) {
            modifiers.push('disabled')
        }
        if (this.markedAsFaulty()) {
            modifiers.push('faulty')
        }
        return modifiers
    }
}
