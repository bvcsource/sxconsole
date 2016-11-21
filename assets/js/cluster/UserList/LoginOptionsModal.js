// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import React, { PropTypes } from 'react'

import { ModalTrigger } from '../../utils/modals/ModalTrigger'
import { ResourceState } from '../../utils/enums'
import { ajax } from '../../utils/ajax'


export default class LoginOptionsModal extends ModalTrigger {
    static propTypes = {
        url: PropTypes.string.isRequired,
    }

    triggerClassName = 'btn btn-default btn-xs'
    modalClassName = 'modal-dialog modal-lg'
    modalTitle = __("Login options")
    triggerText = __("Show login options")

    constructor(props) {
        super(props)
        _.merge(this.state, {
            state: ResourceState.LOADING,
            loginOptions: {},
        })
    }

    onOpen() {
        super.onOpen()
        this.loadData()
    }

    renderModalBody() {
        switch (this.state.state) {
        case ResourceState.LOADING:
            return __("Loading...")
        case ResourceState.ERROR:
            return renderError(this)
        case ResourceState.OK:
            return renderOk(this)
        default:
            throw new Error(`Unknown state: ${this.state.state}`)
        }
    }

    loadData() {
        this.setState({ state: ResourceState.LOADING })
        ajax({
            url: this.props.url,
            success: (data) => {
                this.setState({
                    loginOptions: data,
                    state: ResourceState.OK,
                })
            },
            error: () => {
                this.setState({
                    state: ResourceState.ERROR,
                })
            },
        })
    }
}

function renderError(modal) {
    return (
        <div>
            <span className='text-muted'>
                {__("Failed to load login options.")}
            </span>
            {' '}
            <button className='btn btn-link' onClick={() => modal.loadData()}>
                {__("Retry")}
            </button>
        </div>
    )
}

function renderOk(modal) {
    const options = modal.state.loginOptions
    return (
        <div>
            <h4 children={__("Via S3 protocol")} />
            <KV k={__("S3 endpoint")} v={options.libres3_address} />
            <KV k={__("Access key ID")} v={options.username} />
            <KV k={__("Secret access key")} v={options.token} />
        </div>
    )
}

function KV({ k, v }) {
    return (
        <div>
            <span className='bold' children={k} />
            {': '}
            {v}
        </div>
    )
}
KV.propTypes = {
    k: PropTypes.string.isRequired,
    v: PropTypes.string.isRequired,
}
