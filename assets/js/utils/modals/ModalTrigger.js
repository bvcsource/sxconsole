// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import React, { PropTypes, Component } from 'react'
import ReactModal from 'react-modal'

import { Alert } from '../enums'


const MODAL_CLOSE_TIMEOUT = 200


export class ModalTrigger extends Component {
    static propTypes = {
        triggerClassName: PropTypes.string,
        modalClassName: PropTypes.string,
        triggerDisabled: PropTypes.bool,
        triggerText: PropTypes.string,
    }

    modalTitle = null // eslint-disable-line react/sort-comp
    triggerText = null
    modalClassName = 'modal-dialog'
    triggerClassName = 'btn btn-link'

    state = {
        isModalOpen: false,
        modalAlert: null,
    }

    render() {
        const props = this.getTriggerProps()
        return (
            <button {...props}>
                {props.children}
                {this.renderModal()}
            </button>
        )
    }

    renderModal() {
        return (
            <Modal {...this.getModalProps()}>
                {this.renderModalContent()}
            </Modal>)
    }

    renderModalContent() {
        return (
            <div className='modal-content'>
                <div className='modal-header'>
                    {this.renderModalHeader()}
                </div>
                <div className='modal-body'>
                    {this.renderModalAlert()}
                    {this.renderModalBody()}
                </div>
                <div className='modal-footer'>
                    {this.renderModalFooter()}
                </div>
            </div>)
    }

    renderModalHeader() {
        return (
            <div>
                {this.renderModalHeaderCloseButton()}
                <h4 className='modal-title'>
                    {this.renderModalTitle()}
                </h4>
            </div>)
    }

    renderModalHeaderCloseButton() {
        return (
            <button type='button' className='close' onClick={this.closeModal}>
                <span aria-hidden='true'>&times;</span>
                <span className='sr-only' children={__("Close")} />
            </button>)
    }

    renderModalTitle() {
        if (this.modalTitle) {
            return this.modalTitle
        }
        throw new Error(
            'renderModalTitle was not implemented and modalTitle is not present.')
    }

    renderModalAlert() {
        const alert = this.state.modalAlert
        if (!alert) {
            return
        }

        const alertModifier = `alert-${alert.type.toLowerCase()}`
        const alertClass = `modal-alert alert ${alertModifier}`
        return (
            <div className={alertClass}>
                {alert.msg}
            </div>)
    }

    renderModalBody() { // eslint-disable-line class-methods-use-this
        throw new Error('renderModalBody was not implemented.')
    }

    renderModalFooter() {
        return (
            <div>
                {this.renderCloseButton()}
                {this.renderActionButton()}
            </div>)
    }

    renderCloseButton() {
        const props = {
            type: 'button',
            className: 'btn btn-default',
            onClick: this.closeModal,
            children: __("Cancel"),
        }
        return <button {...props} />
    }

    renderActionButton() { // eslint-disable-line class-methods-use-this
        return null
    }

    getTriggerProps() {
        return {
            type: 'button',
            className: this.getTriggerClassName(),
            disabled: this.isTriggerDisabled(),
            onClick: this.openModal,
            children: this.getTriggerText(),
        }
    }

    getModalProps() {
        return {
            className: this.getModalClassName(),
            isOpen: this.state.isModalOpen,
            onRequestClose: this.closeModal,
            portalClassName: 'ReactModalPortal',
        }
    }

    getTriggerClassName() {
        return this.props.triggerClassName || this.triggerClassName
    }

    getModalClassName() {
        return this.props.modalClassName || this.modalClassName
    }

    isTriggerDisabled() {
        return this.props.triggerDisabled
    }

    getTriggerText() {
        return this.props.triggerText || this.triggerText
    }

    openModal = () => {
        this.setState({ isModalOpen: true })
        this.onOpen()
    }

    closeModal = (cb=null) => {
        this.setState({ isModalOpen: false })
        setTimeout(this.onClose, MODAL_CLOSE_TIMEOUT)
        if (_.isFunction(cb)) {
            setTimeout(cb, MODAL_CLOSE_TIMEOUT)
        }
    }

    onOpen = () => undefined
    onClose = () => {
        this.removeAlert()
    }

    setAlert(type, msg) {
        if (_.includes(Alert, type)) {
            const modalAlert = { type, msg }
            this.setState({ modalAlert })
        } else {
            throw new Error(
                `Unsupported alert type (${type}). Should be one of ${_.values(Alert)}.`)
        }
    }

    removeAlert = () => this.setState({ modalAlert: null })
}

export class Modal extends ReactModal {
    static defaultProps = {
        className: 'modal-dialog',
        style: {
            // Overrides the styles enforced by react-modal
            overlay: {
                backgroundColor: null,
            },
        },
        closeTimeoutMS: MODAL_CLOSE_TIMEOUT,
        shouldCloseOnOverlayClick: true,
    }
}
