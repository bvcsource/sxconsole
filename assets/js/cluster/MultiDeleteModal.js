// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import includes from 'lodash/includes'
import React, { PropTypes } from 'react'

import SubmittableModal from '../utils/modals/SubmittableModal'
import { ajax } from '../utils/ajax'
import { keyMirror, ResourceState } from '../utils/enums'


export const DELETE_STATES = keyMirror(
    'READY',
    'IN_PROGRESS',
    'SUCCESS',
    'ERROR'
)

export default class MultiDeleteModal extends SubmittableModal {
    static propTypes = {
        clusterId: PropTypes.string.isRequired,
        objects: PropTypes.array.isRequired,
        removeObject: PropTypes.func.isRequired,
        getRemoveUrl: PropTypes.func.isRequired,
    }

    submitText = __("Delete")
    submitClassName = 'btn btn-danger'
    modalClassName = 'modal-dialog'
    triggerClassName = 'btn btn-xs btn-danger'

    constructor(props) {
        super(props)
        this.state.state = DELETE_STATES.READY
    }

    renderModalBody() {
        return (
            <div>
                {this.renderMsg()}
                {this.renderObjects()}
            </div>
        )
    }

    renderModalFooter() {
        let footer
        if (this.state.state === DELETE_STATES.SUCCESS) {
            const props = {
                type: 'button',
                className: 'btn btn-default',
                onClick: this.closeModal,
                children: __("Close"),
            }
            footer = <button {...props} />
        } else {
            footer = super.renderModalFooter()
        }
        return footer
    }

    isTriggerDisabled() {
        return this.props.objects.length === 0
    }

    isSubmitDisabled() {
        const disabledWhen = [
            DELETE_STATES.IN_PROGRESS,
            DELETE_STATES.SUCCESS,
        ]
        return includes(disabledWhen, this.state.state)
    }

    onClose = () => {
        this.removeAlert()
        this.setState({ state: DELETE_STATES.READY })
    }

    renderObjects() {
        const items = this.props.objects.map(o => <li key={o} children={o} />)
        return <ul children={items} />
    }

    onSubmit = () => {
        const requests = {}  // { object: ResourceState }
        this.props.objects.forEach((o) => {
            ajax({
                method: 'DELETE',
                url: this.props.getRemoveUrl(this.props.clusterId, o),
                success: () => this.handleSuccess(requests, o),
                error: () => this.handleError(requests, o),
            })
            requests[o] = ResourceState.LOADING
        })
        this.updateStatus(requests)
    }

    handleSuccess(requests, o) {
        requests[o] = ResourceState.OK
        this.props.removeObject(o)
        this.updateStatus(requests)
    }

    handleError(requests, o) {
        requests[o] = ResourceState.ERROR
        this.updateStatus(requests)
    }
}
