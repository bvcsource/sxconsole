// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import { connect } from 'react-redux'

import bytes from '../../utils/bytes'
import FormModalTrigger from '../../utils/modals/FormModalTrigger'
import { addNode } from '../actions'
import { NodeSizeInput, IpInput, InternalIpInput } from '../fields'


@connect(null, { addNode })
export default class AddNodeModal extends FormModalTrigger {
    static propTypes = {
        ...FormModalTrigger.propTypes,
        addNode: PropTypes.func.isRequired,
    }

    modalTitle = __("Adding a new node");
    modalClassName = 'modal-dialog modal-sm'
    triggerText = __("Add node")
    triggerClassName = 'btn btn-default'
    urlName = 'addNode';

    renderModalBody() { // eslint-disable-line class-methods-use-this
        return (
            <div>
                <NodeSizeInput />
                <IpInput />
                <InternalIpInput />
            </div>
        )
    }

    onValidSubmit = (formData) => {
        this.props.addNode({
            ...formData,
            capacity: bytes(formData.capacity),
        })
        this.closeModal()
    }
}
