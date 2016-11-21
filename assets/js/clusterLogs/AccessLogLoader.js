// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import React, { PropTypes, Component } from 'react'

import { ajax } from '../utils/ajax'
import urls from '../utils/urls'


const POLLING_INTERVAL = 5000

function accessLogResultsUrl(id) {
    return window._accessLogResultsUrl.replace('__task_id__', id)
}

export default class AccessLogLoader extends Component {
    static propTypes = {
        taskId: PropTypes.string.isRequired,
    }

    constructor(props) {
        super(props)
        this.state = { task: null }
    }

    componentDidMount() {
        this.pollingLoop()
    }

    render() {
        const taskStatus = _.get(this.state.task, 'status')
        if (taskStatus === 'FAILURE') {
            return (
                <div className='alert alert-danger'>
                    <p>
                        <span className='fa fa-times' />
                        {' '}
                        {__("Failed to fetch acess logs. Try again later.")}
                    </p>
                </div>
            )
        }
        return (
            <div className='alert alert-info'>
                <p>
                    <span className='fa fa-spinner fa-pulse' />
                    {' '}
                    {__("Fetching access logs...")}
                </p>
            </div>
        )
    }

    pollingLoop() {
        const taskUrl = urls.task(this.props.taskId)
        ajax({
            method: 'get',
            url: taskUrl,
            success: (task) => {
                this.setState({ task })
                switch (task.status) {
                case 'SUCCESS':
                    window.location = accessLogResultsUrl(task.id)
                    break
                case 'FAILURE':
                    // TODO
                    break
                default:
                    break
                }
            },
            complete: () => setTimeout(() => this.pollingLoop(), POLLING_INTERVAL),
        })
    }
}
