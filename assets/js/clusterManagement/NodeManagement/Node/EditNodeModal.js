// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import { connect } from 'react-redux'

import bytes from '../../../utils/bytes'
import FormModalTrigger from '../../../utils/modals/FormModalTrigger'
import { NodeSizeInput, IpInput, InternalIpInput } from '../../fields'
import { editNode } from '../../actions'


@connect(null, { editNode })
export default class EditNodeModal extends FormModalTrigger {
    static propTypes = {
        ...FormModalTrigger.propTypes,
        node: PropTypes.object.isRequired,
        pristineNode: PropTypes.object,
        isChanged: PropTypes.bool.isRequired,
        editNode: PropTypes.func.isRequired,
    }

    modalTitle = __("Modifying a node")
    modalClassName = 'modal-dialog modal-sm'
    triggerText = <span className='fa fa-pencil' />
    submitText = __("Modify")

    renderModalBody() {
        const node = this.props.node
        return (
            <div>
                <NodeSizeInput value={bytes(node.capacity)} />
                <IpInput value={node.publicIp} />
                <InternalIpInput value={node.privateIp || ''} />
            </div>
        )
    }

    renderModalFooter() {
        return (
            <div>
                {this.renderCloseButton()}
                {this.props.pristineNode && this.renderRestoreButton()}
                {this.renderActionButton()}
            </div>
        )
    }

    renderRestoreButton() {
        return (
            <button
                className='btn btn-default'
                type='button'
                disabled={!this.props.isChanged}
                onClick={this.restoreNode}
                children={__("Restore")}
            />
        )
    }

    onValidSubmit = (formData) => {
        const payload = {
            ...formData,
            capacity: bytes(formData.capacity),
        }
        this.props.editNode(
            this.props.node.uuid,
            payload
        )
        this.closeModal()
    }

    restoreNode = () => {
        this.props.editNode(
            this.props.node.uuid,
            this.props.pristineNode
        )
        this.closeModal()
    }
}
