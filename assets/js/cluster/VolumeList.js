// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import _ from 'lodash'
import React, { PropTypes } from 'react'
import DOM from 'react-dom'
import bytes from 'bytes'

import urls from '../utils/urls'
import { keyMirror, ResourceState } from '../utils/enums'
import { AjaxMixin } from '../utils/react'
import DeleteVolumesModal from './DeleteVolumesModal'


class Volume {
    constructor(data) {
        _.merge(this, data)
    }

    isEmpty() {
        return this.used_size === 0
    }
}


export default React.createClass({
    propTypes: {
        clusterId: PropTypes.string.isRequired,
        urls: PropTypes.object.isRequired,
    },
    mixins: [AjaxMixin],
    getInitialState() {
        return {
            volumes: {},
            selected: {},
        }
    },
    componentDidUpdate() {
        $(DOM.findDOMNode(this)).trunc() // eslint-disable-line react/no-find-dom-node
    },

    render() {
        const states = this.state._resourceStates
        if (states.volumes === ResourceState.EMPTY) {
            return this.renderEmpty()
        }
        if (_.includes(states, ResourceState.LOADING)) {
            return this.renderLoading()
        }
        if (_.includes(states, ResourceState.ERROR)) {
            return this.renderError()
        }
        return this.renderVolumes()
    },

    renderLoading() {
        return (
            <span className='text-muted'>
                {__("Loading volumes...")}
            </span>
        )
    },
    renderError() {
        return (
            <span>
                <span className='text-muted'>
                    {__("Failed to load volumes.")}
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
                {__("There are no volumes yet")}
            </span>
        )
    },

    renderVolumes() {
        return (
            <div>
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
        // Indexing may be unavailable depending on sxconsole configuration
        const indexing = (this.state.volumes[0].indexing)
            ? <th>{__("Index")}</th>
            : null
        return (
            <thead>
                <tr>
                    <th className='col-name'>{__("Name")}</th>
                    <th>{__("Usage")}</th>
                    <th>{__("Size")}</th>
                    <th>{__("Replicas")}</th>
                    <th>{__("Revs")}</th>
                    {indexing}
                    <th className='col-actions'>{__("Actions")}</th>
                    <th className='col-select'>
                        <input
                            type='checkbox'
                            checked={this.areAllSelected()}
                            onClick={() => this.toggleAllVolumesSelect()}
                        />
                    </th>
                </tr>
            </thead>
        )
    },

    renderTableBody() {
        const rows = this.state.volumes.map((v) => {
            const props = {
                key: v.name,
                clusterId: this.props.clusterId,
                volume: v,
                urls: this.props.urls,
                isSelected: this.isSelected(v.name),
                toggleSelect: () => this.toggleVolumeSelect(v.name),
            }
            return <VolumeRow {...props} />
        })
        return <tbody children={rows} />
    },

    renderSelectionOptions() {
        const props = {
            clusterId: this.props.clusterId,
            objects: _.keys(this.state.selected),
            removeObject: v => this.removeVolume(v),
            getRemoveUrl: urls.volumes,
        }
        return (
            <div className='text-right'>
                <DeleteVolumesModal {...props} />
            </div>
        )
    },

    resources: keyMirror('volumes'),

    loadData() {
        const setVolumesState = _.partial(this.setResourceState, this.resources.volumes)
        setVolumesState(ResourceState.LOADING)
        $.ajax({
            method: 'get',
            url: urls.volumes(this.props.clusterId),
            success: success.bind(this),
            error: error.bind(this),
        })
        function success(data) {
            const state = (_.isEmpty(data.volumes))
                ? ResourceState.EMPTY
                : ResourceState.OK
            const volumes = _.map(data.volumes, d => new Volume(d))
            setVolumesState(state, { volumes })
        }
        function error() {
            setVolumesState(ResourceState.ERROR)
        }
    },

    toggleVolumeSelect(volName) {
        let selected
        if (this.isSelected(volName)) {
            selected = _.omit(this.state.selected, volName)
        } else {
            selected = _.set(this.state.selected, [volName], true)
        }
        this.setState({ selected })
    },

    toggleAllVolumesSelect() {
        let selected
        if (this.areAllSelected()) {
            selected = {}
        } else {
            const toSelect = this.getSelectableVolumes()
            const pairs = _.map(toSelect, v => [v.name, true])
            selected = _.fromPairs(pairs)
        }
        this.setState({ selected })
    },

    getSelectableVolumes() {
        return _.filter(this.state.volumes, v => v.isEmpty())
    },
    isSelected(volName) {
        return _.has(this.state.selected, volName)
    },
    areAllSelected() {
        const selectable = this.getSelectableVolumes()
        const numSelected = _.size(this.state.selected)
        return numSelected === _.size(selectable)
    },

    removeVolume(volName) {
        const volumes = _.reject(this.state.volumes, v => v.name === volName)
        const selected = _.omit(this.state.selected, volName)
        this.setState({ volumes, selected })
    },
})

class VolumeRow extends React.Component {
    static propTypes = {
        volume: React.PropTypes.instanceOf(Volume).isRequired,
        urls: React.PropTypes.object.isRequired,
        isSelected: React.PropTypes.bool.isRequired,
        toggleSelect: React.PropTypes.func.isRequired,
    }

    render() {
        const v = this.props.volume
        return (
            <tr>
                {this.renderNameCol(v)}
                {this.renderUsedSizeCol(v)}
                <td>{bytes(v.size)}</td>
                <td>{v.replicas}</td>
                <td>{v.revisions}</td>
                {this.renderIndexingCol(v)}
                {this.renderActionsCol(v)}
                {this.renderSelectCol(v)}
            </tr>
        )
    }

    renderNameCol(v) {
        let encryption
        if (v.encryption) {
            encryption = (
                <span>
                    {' '}
                    <span className='fa fa-lock' title={__("This volume is encrypted")} />
                </span>
            )
        }
        return (
            <td className='col-name'>
                <span className='js-trunc'>
                    {v.name}
                </span>
                {encryption}
            </td>
        )
    }

    renderUsedSizeCol(v) {
        const percentage = _.round((100 * v.used_size) / v.size, 1)
        return (
            <td>
                {bytes(v.used_size)}
                {' '}
                {`(${percentage}%)`}
            </td>
        )
    }

    renderIndexingCol(v) {
        if (v.indexing_display) {
            return <td>{v.indexing_display}</td>
        }
    }

    renderActionsCol(v) {
        const volumeUrls = this.props.urls
        return (
            <td className='col-actions'>
                <a
                    className='btn btn-default btn-xs'
                    href={volumeUrls.acl(v)}
                    title={__("Manage ACL")}
                >
                    <img
                        className='img-inline'
                        src={urls.static('img/acl.png')}
                    />
                </a>
                &nbsp;
                <a
                    className='btn btn-default btn-xs'
                    href={volumeUrls.edit(v)}
                    title={__("Settings")}
                >
                    <span className='fa fa-cog fa-fw' />
                </a>
                &nbsp;
                <a
                    className='btn btn-danger btn-xs'
                    href={volumeUrls.delete(v)}
                    title={__("Delete")}
                >
                    <span className='fa fa-times fa-fw' />
                </a>
            </td>
        )
    }

    renderSelectCol(v) {
        const props = {
            type: 'checkbox',
            checked: this.props.isSelected,
            onClick: this.props.toggleSelect,
        }
        if (!v.isEmpty()) {
            props.disabled = true
            props.title = __("Cannot mass-delete non-empty volumes.")
        }
        return (
            <td className='col-select'>
                <input {...props} />
            </td>
        )
    }
}
