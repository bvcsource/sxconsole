// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'

import { Alert } from '../utils/enums'
import { ajax } from '../utils/ajax'
import SubmittableModal from '../utils/modals/SubmittableModal'
import CommandPreview from './CommandPreview'


export default class BaseCommandModal extends SubmittableModal {
    static propTypes = {
        node: PropTypes.object.isRequired,
    }

    modalClassName = 'modal-dialog modal-lg'
    urlName = undefined

    constructor(props) {
        super(props)
        this.state.isSubmitting = false
    }

    isSubmitDisabled = () => this.state.isSubmitting

    renderModalBody() {
        return this.renderPreview()
    }

    renderPreview() {
        return (
            <CommandPreview
                url={this.getTaskUrl()}
                data={this.getRequestData()}
            />
        )
    }

    getTaskUrl() {
        return window._sxadmUrls[this.urlName]
    }

    getRequestData() {
        const formData = this.getFormData()
        return { payload: JSON.stringify(formData) }
    }

    getFormData() { // eslint-disable-line class-methods-use-this
        throw new Error('getFormData method was not defined.')
    }

    onSubmit = () => {
        this.setState({ isSubmitting: true })

        const error = () => this.setAlert(
            Alert.ERROR,
            __("Failed to queue the task.")
        )
        const success = data => (window.location = data.next)
        const complete = () => this.setState({ isSubmitting: false })

        ajax({
            method: 'post',
            url: this.getTaskUrl(),
            data: this.getRequestData(),
            success,
            error,
            complete,
        })
    }
}
