// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import Formsy from 'formsy-react'

import { ModalTrigger } from './ModalTrigger'


export default class FormModalTrigger extends ModalTrigger {
    submitText = null

    renderModalContent() {
        return (
            <Formsy.Form
                ref='form'
                onChange={this.onChange}
                onValid={this.onValid}
                onInvalid={this.onInvalid}
                onValidSubmit={this.onValidSubmit}
                children={super.renderModalContent()}
            />
        )
    }

    renderActionButton() {
        return (
            <button
                {...this.getActionButtonProps()}
                children={this.submitText || this.triggerText}
            />
        )
    }

    getActionButtonProps() {
        const props = {
            type: 'submit',
            className: 'btn btn-primary',
            disabled: !this.state.canSubmit,
        }
        return props
    }

    onValid = () => {
        this.updateFormData()
        this.enableSubmit()
    }

    onInvalid = () => {
        this.updateFormData()
        this.disableSubmit()
    }

    onValidSubmit = () => {
        this.disableSubmit()
    }

    getFormData() {
        return this.state.formData
    }

    updateFormData = () => {
        const form = this.refs.form
        const formData = form.getCurrentValues()
        this.setState({ formData })
    }

    enableSubmit = () => this.setState({ canSubmit: true })
    disableSubmit = () => this.setState({ canSubmit: false })
}
