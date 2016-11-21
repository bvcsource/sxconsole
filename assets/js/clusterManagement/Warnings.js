// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import React, { PropTypes } from 'react'


export default function Warnings({ nodes }) {
    let handler
    if (_.some(nodes, n => n.operation)) {
        handler = RebalanceStatus
    } else {
        handler = OtherWarnings
    }
    return handler({ nodes })
}
Warnings.propTypes = {
    nodes: PropTypes.array.isRequired,
}

function RebalanceStatus({ nodes }) {
    const rebalancingNodes = _.filter(nodes, 'operation')
    const operation = _.capitalize(rebalancingNodes[0].operation.type)
    return (
        <div className='alert alert-warning'>
            <h4>
                <span className='fa fa-spinner fa-pulse' />
                {' '}
                {__("{{operation}} in progress", { operation })}
            </h4>
            <ul>
                {rebalancingNodes.map((node) => {
                    const props = {
                        node,
                        key: node.uuid,
                        message: node.operation.info,
                    }
                    return <NodeListItem {...props} />
                })}
            </ul>
        </div>
    )
}
RebalanceStatus.propTypes = {
    nodes: PropTypes.array.isRequired,
}


function OtherWarnings({ nodes }) {
    const problematicNodes = _.filter(nodes, n => n.isFaulty || n.isDown)
    if (_.isEmpty(problematicNodes)) {
        return <div />
    }

    return (
        <div className='alert alert-danger'>
            <h4 children={__("There are nodes that need your attention!")} />
            <p children={__("Certain cluster management operations may be unavailable.")} />
            <ul
                children={problematicNodes.map((node) => {
                    let message
                    if (node.isFaulty) {
                        message = __("This node is faulty and needs to be replaced.")
                    } else if (node.isDown) {
                        message = __("This node is not responding.")
                    }

                    const props = {
                        message,
                        node,
                        key: node.uuid,
                    }
                    return <NodeListItem {...props} />
                })}
            />
        </div>
    )
}
OtherWarnings.propTypes = {
    nodes: PropTypes.array.isRequired,
}


function NodeListItem({ node, message }) {
    return (
        <li>
            <span className='bold' children={node.publicIp} />
            {': '}
            {message}
        </li>
    )
}
NodeListItem.propTypes = {
    node: PropTypes.object.isRequired,
    message: PropTypes.string.isRequired,
}
