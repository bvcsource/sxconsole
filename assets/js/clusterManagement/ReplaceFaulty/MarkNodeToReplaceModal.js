// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import { connect } from 'react-redux'

import FormModalTrigger from '../../utils/modals/FormModalTrigger'
import { IpInput, InternalIpInput } from '../fields'
import { markNodeToReplace, cancelNodeReplacement } from '../actions'


@connect(null, { markNodeToReplace, cancelNodeReplacement })
export default class MarkNodeToReplaceModal extends FormModalTrigger {
    static propTypes = {
        ...FormModalTrigger.propTypes,
        node: PropTypes.object.isRequired,
    }

    modalTitle = __("Set up node replacement")
    modalClassName = 'modal-dialog modal-sm'
    triggerClassName = 'btn btn-default btn-xs'
    triggerText = <span className='fa fa-wrench' />
    submitText = __("Ok")

    renderModalBody() {
        const { node } = this.props
        return (
            <div>
                <IpInput value={node.newPublicIp || node.publicIp} />
                <InternalIpInput value={node.newInternalIp || node.InternalIp || ''} />
            </div>
        )
    }

    renderModalFooter() {
        return (
            <div>
                {this.renderCloseButton()}
                {this.renderCancelReplacementButton()}
                {this.renderActionButton()}
            </div>
        )
    }

    renderCancelReplacementButton() {
        return (
            <button
                className='btn btn-default'
                disabled={!this.props.node.newPublicIp}
                onClick={this.cancelNodeReplacement}
                children={__("Undo")}
            />
        )
    }

    onValidSubmit = (formData) => {
        this.props.markNodeToReplace(
            this.props.node.uuid,
            formData.publicIp,
            formData.privateIp,
        )
        this.closeModal()
    }

    cancelNodeReplacement = () => {
        this.props.cancelNodeReplacement(this.props.node.uuid)
        this.closeModal()
    }
}
