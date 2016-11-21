// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { getNode, getPristineNode } from '../reducers'
import NodeInfoModal from '../NodeInfoModal'
import NodeComponent from '../components/Node'
import MarkNodeToReplaceModal from './MarkNodeToReplaceModal'


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
        const { node } = this.props
        const disabled = this.isDisabled()
        return (
            <div style={{ float: 'right' }}>
                <NodeInfoModal
                    node={node}
                    triggerClassName={'btn btn-default btn-xs'}
                    triggerDisabled={false}
                />
                {' '}
                <MarkNodeToReplaceModal node={node} triggerDisabled={disabled} />
            </div>
        )
    }

    displayNodeStatus() {
        if (this.isDisabled()) {
            return __("Healthy")
        }
        if (this.markedForReplacement()) {
            return __(
                "New ip: {{ip}}",
                { ip: this.props.node.newPublicIp },
            )
        }
        return __("Faulty")
    }

    isDisabled = () => !this.props.node.isFaulty
    markedForReplacement = () => this.props.node.markedForReplacement

    getNodeModifiers() {
        const modifiers = []
        if (this.isDisabled()) {
            modifiers.push('disabled')
            modifiers.push('new')
        }
        if (this.markedForReplacement()) {
            modifiers.push('new')
        }
        return modifiers
    }
}
