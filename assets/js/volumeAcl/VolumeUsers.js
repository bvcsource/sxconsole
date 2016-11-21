// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import _ from 'lodash'
import React, { PropTypes } from 'react'

import urls from '../utils/urls'
import { ajax } from '../utils/ajax'
import { keyMirror, ResourceState } from '../utils/enums'
import { AjaxMixin } from '../utils/react'


/* Return an identificator for user permission */
const permKey = (email, type) => `${email}-${type}`

const VolumeUsers = React.createClass({
    propTypes: {
        clusterId: PropTypes.number.isRequired,
        volumeName: PropTypes.string.isRequired,
    },
    mixins: [AjaxMixin],

    getInitialState() {
        return {
            users: [],
            acl: {},
            pendingRequests: {},
        }
    },

    render() {
        const states = this.state._resourceStates
        if (states.acl === ResourceState.EMPTY) {
            return this.renderEmpty()
        }
        if (_.includes(states, ResourceState.LOADING)) {
            return this.renderLoading()
        }
        if (_.includes(states, ResourceState.ERROR)) {
            return this.renderError()
        }
        return this.renderAcl()
    },

    renderLoading() {
        return (
            <span className='text-muted'>
                {__("Loading users...")}
            </span>
        )
    },

    renderError() {
        return (
            <span>
                <span className='text-muted'>
                    {__("Failed to load users.")}
                </span>
                {' '}
                <button className='btn btn-link' onClick={this.loadData}>
                    {__("Retry")}
                </button>
            </span>
        )
    },

    renderEmpty() {
        return (
            <span className='text-muted'>
                {__("There are no users yet")}
            </span>
        )
    },

    renderAcl() {
        return (
            <table className='table table-striped'>
                <thead>
                    <tr>
                        <th>{__("Username")}</th>
                        <th className='text-right'>{__("Permissions")}</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.users.map(this.renderRow)}
                </tbody>
            </table>
        )
    },

    renderRow(email) {
        const perm = this.state.acl[email]
        return (
            <tr key={perm.email}>
                <td>{perm.email}</td>
                <td className='text-right'>
                    <div className='btn-group'>
                        {this.renderPermBtn(perm, 'read')}
                        {this.renderPermBtn(perm, 'write')}
                        {this.renderPermBtn(perm, 'manager')}
                    </div>
                </td>
            </tr>
        )
    },

    renderPermBtn(perm, type) {
        const email = perm.email
        const btnClass = (perm[type])
            ? 'btn btn-success'
            : 'btn btn-default'
        let typeName
        let typeDesc
        switch (type) {
        case 'read':
            typeName = __("Read")
            typeDesc = __("The user can read files on the volume")
            break
        case 'write':
            typeName = __("Write")
            typeDesc = __("The user can modify files on the volume")
            break
        case 'manager':
            typeName = __("Manager")
            typeDesc = __("The user can manage permissions of other users on this volume")
            break
        default:
            throw new Error(`Unknown type value: ${type}`)
        }
        const disabled = perm.is_reserved ||
            this.state.pendingRequests[permKey(email, type)]
        return (
            <button
                key={permKey(email, type)}
                className={btnClass}
                type='button'
                disabled={disabled}
                style={{ cursor: 'pointer' }}
                title={typeDesc}
                onClick={this.getButtonHandler(email, type)}
                children={typeName}
            />
        )
    },

    resources: keyMirror('acl'),
    loadData() {
        const setAclState = _.partial(this.setResourceState, this.resources.acl)
        setAclState(ResourceState.LOADING)
        $.ajax({
            method: 'get',
            url: urls.volumeAcl(this.props.clusterId, this.props.volumeName),
            success: success.bind(this),
            error: error.bind(this),
        })
        function success(data) {
            const state = (_.isEmpty(data.acl))
                ? ResourceState.EMPTY
                : ResourceState.OK
            setAclState(state, {
                users: _.map(data.acl, 'email'),
                acl: _.keyBy(data.acl, 'email'),
            })
        }
        function error() {
            setAclState(ResourceState.ERROR)
        }
    },

    getButtonHandler(email, type) {
        return () => {
            const options = {
                method: 'patch',
                url: urls.volumeAcl(this.props.clusterId, this.props.volumeName, email),
                data: this.getAclData(email, type),
                success: success.bind(this),
                complete: complete.bind(this),
            }
            function success(data) {
                // Update the perm
                this.state.acl[email] = data
                this.setState({ acl: this.state.acl })
            }
            function complete() {
                // Always unregister from pendingRequests
                this.state.pendingRequests[permKey(email, type)] = false
                this.setState({ pendingRequests: this.state.pendingRequests })
            }

            // Register the action to pendingRequests
            this.state.pendingRequests[permKey(email, type)] = true
            this.setState({ pendingRequests: this.state.pendingRequests })

            // Send the request
            ajax(options)
        }
    },

    getAclData(email, type) {
        // Return new ACL values after granting/revoking permission
        const data = {
            email,
            [type]: !this.state.acl[email][type],
        }
        if (data.write) {
            // If we grant write access, grant read automatically.
            data.read = true
        }
        if (data.manager) {
            // If we grant manager access, grant r/w automatically.
            data.read = data.write = true
        }
        return data
    },
})

export default VolumeUsers
