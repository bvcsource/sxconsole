// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import get from 'lodash/get'
import React, { PropTypes } from 'react'


export default function TaskIcon({ task }) {
    const statusClass = {
        SUCCESS: 'fa fa-check',
        FAILURE: 'fa fa-times',
    }
    const defaultClass = 'fa fa-spinner fa-pulse'

    const status = get(task, 'status')
    const className = get(statusClass, status, defaultClass)
    return <span className={className} />
}
TaskIcon.propTypes = {
    task: PropTypes.object,
}
