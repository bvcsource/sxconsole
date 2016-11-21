// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import { ModalTrigger } from './ModalTrigger'


export default class SubmittableModal extends ModalTrigger {
    submitText = null
    submitClassName = 'btn btn-primary'

    renderActionButton() {
        return (
            <button {...this.getActionButtonProps()}>
                {this.submitText || this.triggerText}
            </button>)
    }

    getActionButtonProps() {
        return {
            type: 'submit',
            className: this.submitClassName,
            onClick: e => this.onSubmit(e),
            disabled: this.isSubmitDisabled(),
        }
    }

    isSubmitDisabled() { // eslint-disable-line class-methods-use-this
        return false
    }

    onSubmit() {
        this.closeModal(this.props.onSubmit)
    }
}
