// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import { render } from 'react-dom'

import TaskStatus from './TaskStatus'


const mount = document.getElementById('task-status')
const data = JSON.parse(mount.dataset.init)
render(
    <TaskStatus {...data} />,
    mount
)
