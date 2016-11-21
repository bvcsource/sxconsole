// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { Component } from 'react'

import { ajax } from '../utils/ajax'


export default class ManageCluster extends Component {
    static propTypes = {
        cluster: React.PropTypes.object.isRequired,
    }

    state = {
        isAdministrated: this.props.cluster.is_administrated,
        isLoading: false,
    }

    render() {
        return (
            <tr>
                <td children={this.props.cluster.name} />
                <td className='text-right'>
                    <button
                        className={this.getButtonClassName()}
                        disabled={this.state.isLoading}
                        onClick={this.handleButtonClick}
                        children={(this.state.isAdministrated)
                            ? __("Remove from admins")
                            : __("Make administrator")}
                    />
                </td>
            </tr>
        )
    }

    getButtonClassName() {
        return (this.state.isAdministrated)
            ? 'btn btn-success'
            : 'btn btn-default'
    }

    handleButtonClick = () => {
        this.setState({ isLoading: true })
        const options = {
            method: 'post',
            data: {
                cluster_id: this.props.cluster.id,
                is_administrated: !this.state.isAdministrated,
            },
            success: () => this.setState({
                isAdministrated: !this.state.isAdministrated,
            }),
            complete: () => this.setState({
                isLoading: false,
            }),
        }
        ajax(options)
    }
}

