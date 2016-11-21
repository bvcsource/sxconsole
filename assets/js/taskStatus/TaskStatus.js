// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import _ from 'lodash'
import React, { PropTypes, Component } from 'react'
import moment from 'moment'

import urls from '../utils/urls'
import Task from './Task'
import TaskIcon from './TaskIcon'


const longFormat = moment.localeData().longDateFormat('LLLL')
const enDash = '\u2013'


export default class TaskStatus extends Component {
    static propTypes = {
        uuid: PropTypes.string.isRequired,
    }

    constructor(props) {
        super(props)
        this.state = {
            task: null,
            lastUpdate: null,
        }
    }

    componentDidMount() {
        this.taskPollingLoop()
        this.refreshDatesLoop()
    }

    render() {
        return (
            <div>
                {this.renderHeader()}
                {this.renderTaskStatus()}
            </div>)
    }

    renderHeader() {
        return (
            <header className='page-title'>
                <TaskIcon task={this.state.task} />
                {' '}
                {__('Task status')}
            </header>
        )
    }

    renderTaskStatus() {
        const task = this.state.task
        if (!task) {
            return (
                <span className='lead text-muted'>
                    {__("Loading...")}
                </span>)
        }
        const statusColor = getTaskColor(task)
        return (
            <table className='table'>
                <tbody>
                    <tr>
                        <th>{__("Task")}</th>
                        <td>
                            {task.displayType}
                            <small className='text-muted'>
                                {' '}
                                {__("(ID: {{id}})", { id: task.id })}
                            </small>
                        </td>
                    </tr>
                    <tr className={statusColor}>
                        <th>{__("Status")}</th>
                        <td>
                            {task.status}
                            {task.ready ? null : this.renderLastUpdate()}
                        </td>
                    </tr>
                    <tr>
                        <th>{__("Added")}</th>
                        <td>{displayDate(task.queueDate)}</td>
                    </tr>
                    <tr>
                        <th>{__("Start date")}</th>
                        <td>{displayDate(task.startDate)}</td>
                    </tr>
                    <tr>
                        <th>{__("End date")}</th>
                        <td>{displayDate(task.endDate)}</td>
                    </tr>
                    <tr>
                        <th>{__("Details")}</th>
                        <td>{task.info || enDash}</td>
                    </tr>
                </tbody>
            </table>)
    }

    renderLastUpdate() {
        const lastUpdate = this.state.lastUpdate.fromNow()
        const text = __("Last check: {{when}}", { when: lastUpdate })
        return (
            <small className='text-muted'>
                {` (${text})`}
            </small>)
    }

    taskPollingLoop = () => {
        const onTaskLoad = () => {
            const isReady = _.get(this.state.task, 'ready')
            if (!isReady) {
                setTimeout(this.taskPollingLoop, 1000)
            }
        }
        this.loadTask(onTaskLoad)
    }

    refreshDatesLoop = () => {
        // Re-render relative dates (e.g. 'a few seconds ago')
        this.forceUpdate()
        setTimeout(this.updateDatesLoop, 5000)
    }

    loadTask(cb=noop) {
        $.ajax({
            method: 'get',
            url: urls.task(this.props.uuid),
            success: data => this.setState({
                task: new Task(data),
                lastUpdate: moment(),
            }),
            complete: cb,
        })
    }
}

function displayDate(date) {
    if (!date) {
        return enDash
    }
    return (
        <time dateTime={date.format()} title={date.format(longFormat)}>
            {date.fromNow()}
        </time>
    )
}

function noop() {}

function getTaskColor(task) {
    const statusColor = {
        SUCCESS: 'success',
        FAILURE: 'danger',
    }
    const defaultColor = ''

    const status = _.get(task, 'status')
    const color = _.get(statusColor, status, defaultColor)
    return color
}
