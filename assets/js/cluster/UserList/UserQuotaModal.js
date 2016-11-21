// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, Component } from 'react'
import { Form } from 'formsy-react'
import Modal from 'react-modal'

import { ajax } from '../../utils/ajax'
import bytes from '../../utils/bytes'
import urls from '../../utils/urls'
import SizeInput from '../../components/SizeInput'


export default class UserQuotaModal extends Component {
    static propTypes = {
        isOpen: PropTypes.bool.isRequired,
        clusterId: PropTypes.string.isRequired,
        user: PropTypes.object,
        closeModal: PropTypes.func.isRequired,
        closeTimeoutMS: PropTypes.number,
    }

    static defaultProps = {
        closeTimeoutMS: 200,
    }

    state = {
        submitDisabled: false,
        submitError: null,
    }

    render() {
        if (!this.props.user) {
            return null
        }
        return (
            <Modal
                className='modal-dialog modal-sm'
                overlayClassName='ReactModal__Overlay'
                shouldCloseOnOverlayClick
                isOpen={this.props.isOpen}
                closeTimeoutMS={this.props.closeTimeoutMS}
                onRequestClose={this.props.closeModal}
            >
                <Form
                    ref={n => (this.form = n)}
                    onValid={this.enableSubmit}
                    onInvalid={this.disableSubmit}
                    onValidSubmit={this.onValidSubmit}
                >
                    <div className='modal-content'>
                        <ModalHeader
                            close={this.props.closeModal}
                            user={this.props.user}
                        />

                        <div className='modal-body'>
                            <fieldset>
                                <SizeInput
                                    autoFocus
                                    label={__("Quota")}
                                    name='quota'
                                    value={bytes(this.props.user.quota)}
                                />
                            </fieldset>
                            {this.state.submitError && <FormError msg={this.state.submitError} />}
                        </div>
                        <div className='modal-footer'>
                            <FooterCloseButton close={this.props.closeModal} />
                            {' '}
                            <button
                                className='btn btn-primary'
                                disabled={!this.isChanged() || this.state.submitDisabled}
                                children={__("Submit")}
                            />
                        </div>
                    </div>
                </Form>
            </Modal>
        )
    }

    isChanged = () => this.form && this.form.isChanged()
    enableSubmit = () => this.setState({ submitDisabled: false })
    disableSubmit = () => this.setState({ submitDisabled: true })
    onValidSubmit = (model) => {
        const request = {
            method: 'PATCH',
            url: urls.users(this.props.clusterId, this.props.user.email),
            data: {
                quota: bytes(model.quota),
            },
            success: (data) => {
                this.props.user.quota = data.quota
                this.props.closeModal()
            },
            error: () => {
                this.setState({ submitError: __("Failed to submit the form.") })
                this.enableSubmit()
            },
        }
        this.setState({ submitError: null })
        this.disableSubmit()
        ajax(request)
    }
}


function ModalHeader({ close, user }) {
    return (
        <div className='modal-header'>
            <HeaderCloseButton close={close} />
            <h4 className='modal-title' children={user.email} />
        </div>
    )
}
ModalHeader.propTypes = {
    close: PropTypes.func.isRequired,
    user: PropTypes.object,
}


function HeaderCloseButton({ close }) {
    return (
        <button type='button' className='close' onClick={close}>
            <span aria-hidden='true'>&times;</span>
            <span className='sr-only' children={__("Close")} />
        </button>
    )
}
HeaderCloseButton.propTypes = {
    close: PropTypes.func.isRequired,
}


function FooterCloseButton({ close }) {
    return (
        <button
            type='button'
            className='btn btn-default'
            onClick={close}
            children={__("Close")}
        />
    )
}
FooterCloseButton.propTypes = {
    close: PropTypes.func.isRequired,
}


function FormError({ msg }) {
    if (!msg) {
        return null
    }
    return <div className='alert alert-danger' children={msg} />
}
FormError.propTypes = {
    msg: PropTypes.string.isRequired,
}
