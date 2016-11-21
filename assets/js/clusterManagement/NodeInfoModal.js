// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import React, { PropTypes } from 'react'

import { ModalTrigger } from '../utils/modals/ModalTrigger'
import { displayNodeStatus } from './NodeStatus'


export default class NodeInfoModal extends ModalTrigger {
    static propTypes = {
        node: PropTypes.object.isRequired,
    }

    modalTitle = __("Node details")
    triggerText = <span className='fa fa-info-circle' />

    renderModalBody() {
        const { node } = this.props
        return (
            <div>
                <NodeField
                    label={__("Status")}
                    value={displayNodeStatus(node)}
                />
                <NodeField
                    label={__("Node UUID")}
                    value={node.uuid}
                />
                <NodeField
                    label={__("Node IP")}
                    value={node.publicIp}
                />
                <NodeField
                    label={__("Internal IP")}
                    value={node.privateIp}
                />
                <NodeField
                    label={__("Capacity")}
                    value={bytes(node.capacity)}
                />
                <NodeField
                    label={__("SX version")}
                    value={node.sxVersion}
                />
            </div>
        )
    }
}

const enDash = '\u2013'
const NodeField = ({ label, value }) => (
    <div>
        <span className='bold' children={`${label}:`} />
        {' '}
        {value || enDash}
    </div>
)
NodeField.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.node,
}
