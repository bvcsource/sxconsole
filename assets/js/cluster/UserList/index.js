// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import bytes from 'bytes'
import _ from 'lodash'
import React, { PropTypes } from 'react'

import urls from '../../utils/urls'
import { keyMirror, ResourceState } from '../../utils/enums'
import { AjaxMixin } from '../../utils/react'
import DeleteUsersModal from './DeleteUsersModal'
import LoginOptionsModal from './LoginOptionsModal'
import UserQuotaModal from './UserQuotaModal'


export default React.createClass({
    propTypes: {
        clusterId: React.PropTypes.string.isRequired,
        urls: React.PropTypes.object.isRequired,
        showLoginOptions: React.PropTypes.bool.isRequired,
    },
    mixins: [AjaxMixin],

    getInitialState() {
        return {
            users: [],
            selected: {},
            quotaModalOpen: false,
            quotaModalUser: null,
        }
    },

    render() {
        const states = this.state._resourceStates
        if (states.users === ResourceState.EMPTY) {
            return this.renderEmpty()
        }
        if (_.includes(states, ResourceState.LOADING)) {
            return this.renderLoading()
        }
        if (_.includes(states, ResourceState.ERROR)) {
            return this.renderError()
        }
        return this.renderUsers()
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

    renderUsers() {
        return (
            <div>
                <UserQuotaModal
                    clusterId={this.props.clusterId}
                    isOpen={this.state.quotaModalOpen}
                    user={this.state.quotaModalUser}
                    closeModal={this.closeQuotaModal}
                />
                <div className='table-responsive'>
                    <table className='table-common table-hover'>
                        {this.renderTableHeader()}
                        {this.renderTableBody()}
                    </table>
                </div>
                {this.renderSelectionOptions()}
            </div>
        )
    },

    renderTableHeader() {
        return (
            <thead>
                <tr>
                    <th className='col-name'>{__("Username")}</th>
                    <th children={__("Quota")} />
                    <th className='col-actions'>{__("Actions")}</th>
                    <th className='col-select'>
                        <input
                            type='checkbox'
                            checked={this.areAllSelected()}
                            onClick={() => this.toggleAllUsersSelect()}
                        />
                    </th>
                </tr>
            </thead>
        )
    },

    renderTableBody() {
        return (
            <tbody>
                {this.state.users.map((u) => {
                    const props = {
                        key: u.email,
                        clusterId: this.props.clusterId,
                        user: u,
                        urls: this.props.urls,
                        isSelected: this.isSelected(u.email),
                        toggleSelect: () => this.toggleUserSelect(u.email),
                        showLoginOptions: this.props.showLoginOptions,
                        openQuotaModal: this.openQuotaModal,
                    }
                    return <UserRow {...props} />
                })}
            </tbody>
        )
    },

    renderSelectionOptions() {
        const props = {
            clusterId: this.props.clusterId,
            objects: _.keys(this.state.selected),
            removeObject: u => this.removeUser(u),
            getRemoveUrl: urls.users,
        }
        return (
            <div className='text-right'>
                <DeleteUsersModal {...props} />
            </div>
        )
    },

    resources: keyMirror('users'),

    loadData() {
        this.loadUsers()
    },

    loadUsers() {
        const setUsersState = _.partial(this.setResourceState, this.resources.users)
        setUsersState(ResourceState.LOADING)
        $.ajax({
            method: 'get',
            url: urls.users(this.props.clusterId),
            success: success.bind(this),
            error: error.bind(this),
        })
        function success(data) {
            const state = (_.isEmpty(data.users))
                ? ResourceState.EMPTY
                : ResourceState.OK
            setUsersState(state, { users: data.users })
        }
        function error() {
            setUsersState(ResourceState.ERROR)
        }
    },

    toggleUserSelect(email) {
        let selected
        if (this.isSelected(email)) {
            selected = _.omit(this.state.selected, email)
        } else {
            selected = _.set(this.state.selected, [email], true)
        }
        this.setState({ selected })
    },

    toggleAllUsersSelect() {
        let selected
        if (this.areAllSelected()) {
            selected = {}
        } else {
            const toSelect = this.getSelectableUsers()
            const pairs = _.map(toSelect, u => [u.email, true])
            selected = _.fromPairs(pairs)
        }
        this.setState({ selected })
    },

    getSelectableUsers() {
        return _.reject(this.state.users, 'is_reserved')
    },
    isSelected(email) {
        return _.has(this.state.selected, email)
    },
    areAllSelected() {
        const selectable = this.getSelectableUsers()
        const numSelected = _.size(this.state.selected)
        return numSelected === _.size(selectable)
    },

    removeUser(email) {
        const users = _.reject(this.state.users, u => u.email === email)
        const selected = _.omit(this.state.selected, email)
        this.setState({ users, selected })
    },

    openQuotaModal(user) {
        return () => this.setState({ quotaModalOpen: true, quotaModalUser: user })
    },

    closeQuotaModal() {
        this.setState({ quotaModalOpen: false })
    },
})

class UserRow extends React.Component {
    static propTypes = {
        user: React.PropTypes.object.isRequired,
        urls: React.PropTypes.object.isRequired,
        isSelected: React.PropTypes.bool.isRequired,
        toggleSelect: React.PropTypes.func.isRequired,
        showLoginOptions: React.PropTypes.bool.isRequired,
        openQuotaModal: PropTypes.func.isRequired,
    }

    render() {
        const u = this.props.user
        return (
            <tr>
                <UserEmailColumn user={u} />
                <UserQuotaColumn user={u} />
                {this.renderActionsCol(u)}
                {this.renderSelectCol(u)}
            </tr>
        )
    }

    renderActionsCol(u) {
        let actions
        if (u.is_reserved) {
            actions = <td className='col-actions'>&ndash;</td>
        } else {
            const userUrls = this.props.urls
            actions = (
                <td className='col-actions'>
                    <button
                        className='btn btn-default btn-xs'
                        type='button'
                        onClick={this.props.openQuotaModal(u)}
                        children={__("Manage quota")}
                    />
                    {' '}
                    <a className='btn btn-default btn-xs' href={userUrls.resetPassword(u)}>
                        {__("Reset password")}
                    </a>
                    {' '}
                    {this.renderLoginOptions(u)}
                    {' '}
                    <a className='btn btn-danger btn-xs' href={userUrls.delete(u)}>
                        {__("Delete")}
                    </a>
                </td>
            )
        }
        return actions
    }

    renderLoginOptions(u) {
        return (this.props.showLoginOptions)
            ? <LoginOptionsModal url={this.props.urls.loginOptions(u)} />
            : null
    }

    renderSelectCol(u) {
        const props = {
            type: 'checkbox',
            checked: this.props.isSelected,
            onClick: this.props.toggleSelect,
        }
        if (u.is_reserved) {
            props.disabled = true
            props.title = __("Cannot delete reserved users.")
        }
        return (
            <td className='col-select'>
                <input {...props} />
            </td>
        )
    }

}

const UserEmailColumn = ({ user }) => <td className='col-name' children={user.email} />
UserEmailColumn.propTypes = {
    user: PropTypes.object.isRequired,
}

const UserQuotaColumn = ({ user }) => <td children={displayQuota(user)} />
UserQuotaColumn.propTypes = {
    user: PropTypes.object.isRequired,
}

function displayQuota(user) {
    return __(
        "{{quota}} ({{quotaUsed}} used)", {
            quota: bytes(user.quota),
            quotaUsed: bytes(user.quota_used),
        }
    )
}
