// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import isMatch from 'lodash/isMatch'
import bytes from 'bytes'
import React, { PropTypes, Component } from 'react'
import { connect } from 'react-redux'

import { getNode, getPristineNode } from '../../reducers'
import { nodeDragSource } from '../dnd'
import EditNodeModal from './EditNodeModal'
import RemoveNodeButton from './RemoveNodeButton'
import RestoreNodeButton from './RestoreNodeButton'
import NodeInfoModal from '../../NodeInfoModal'
import NodeComponent from '../../components/Node'


export default function ZoneNode({ nodeId, zoneName }) {
    return (
        <div className='col-xs-6 col-md-6 col-lg-4'>
            <DraggableNode nodeId={nodeId} zoneName={zoneName} />
        </div>
    )
}
ZoneNode.propTypes = {
    nodeId: PropTypes.string.isRequired,
    zoneName: PropTypes.string.isRequired, // required for dnd
}

const mapStateToProps = (state, ownProps) => ({
    node: getNode(state, ownProps.nodeId),
    pristineNode: getPristineNode(state, ownProps.nodeId),
})

@connect(mapStateToProps)
@nodeDragSource
class DraggableNode extends Component {
    static propTypes = {
        nodeId: PropTypes.string.isRequired,
        // zoneName is required for dnd
        zoneName: PropTypes.string.isRequired, // eslint-disable-line react/no-unused-prop-types
        pristineNode: PropTypes.object,
        node: PropTypes.object.isRequired,
        connectDragSource: PropTypes.func.isRequired,
        isDragging: PropTypes.bool.isRequired,
    }

    render() {
        return this.props.connectDragSource(
            <div>
                <NodeComponent classModifiers={this.getNodeModifiers()}>
                    {this.renderNodeButtons()}
                    {this.renderNodeInfo()}
                </NodeComponent>
            </div>
        )
    }

    renderNodeInfo() {
        const { node } = this.props
        return (
            <div>
                <div className='bold' children={node.publicIp} />
                <div>
                    {node.isDown ? __("Offline") : __("Online")}
                    {', '}
                    {bytes(node.capacity)}
                </div>
            </div>
        )
    }

    renderNodeButtons() {
        const { nodeId } = this.props
        const props = {
            node: this.props.node,
            triggerDisabled: this.isRemoved(),
            triggerClassName: 'btn btn-default btn-xs',
        }
        return (
            <div style={{ float: 'right' }}>
                <NodeInfoModal
                    {...props}
                    triggerDisabled={false}
                />
                {' '}
                <EditNodeModal
                    {...props}
                    pristineNode={this.props.pristineNode}
                    isChanged={this.isChanged()}
                />
                {' '}
                {this.isRemoved()
                    ? <RestoreNodeButton nodeId={nodeId} />
                    : <RemoveNodeButton nodeId={nodeId} />
                }
            </div>
        )
    }

    isNew() {
        return this.props.node.isNew
    }

    isChanged() {
        return !this.isNew() && !isMatch(
            this.props.node,
            this.props.pristineNode)
    }

    isRemoved() {
        return this.props.node.isRemoved
    }

    getNodeModifiers() {
        const modifiers = []
        if (this.props.isDragging) {
            modifiers.push('dragging')
        }
        if (this.isNew()) {
            modifiers.push('new')
        }
        if (this.isRemoved()) {
            modifiers.push('disabled')
        } else {
            modifiers.push('draggable')
        }
        if (this.isChanged()) {
            modifiers.push('changed')
        }
        return modifiers
    }
}
