// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import HTML5Backend from 'react-dnd-html5-backend'
import { DragDropContext, DragSource, DropTarget } from 'react-dnd'


export const nodeDndContext = DragDropContext(HTML5Backend)

const itemTypes = {
    NODE: 'NODE',
}


// Drag

const nodeDragSpec = {
    beginDrag(props) {
        return {
            nodeId: props.nodeId,
            zoneName: props.zoneName,
        }
    },
    isDragging(props, monitor) {
        return props.nodeId === monitor.getItem().nodeId
    },
    canDrag(props) {
        return !props.node.isRemoved
    },
}

const nodeDragCollector = (connect, monitor) => ({
    connectDragSource: connect.dragSource(),
    isDragging: monitor.isDragging(),
})

export const nodeDragSource = DragSource(
    itemTypes.NODE,
    nodeDragSpec,
    nodeDragCollector
)


// Drop

const nodeDropSpec = {
    hover(props, monitor) {
        const item = monitor.getItem()
        // `item` is the node we're dragging.
        // `props` is what we're hovering over.
        if (item.zoneName !== props.zoneName) {
            props.moveNode(item.nodeId, item.zoneName, props.zoneName)
            item.zoneName = props.zoneName
        }
    },
}

const nodeDropCollector = connect => ({
    connectDropTarget: connect.dropTarget(),
})

export const nodeDropTarget = DropTarget(
    itemTypes.NODE,
    nodeDropSpec,
    nodeDropCollector
)
