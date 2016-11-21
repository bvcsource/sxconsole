// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import { render } from 'react-dom'

import SizeWidget from './SizeWidget'


const mount = document.getElementById('size-widget')
const data = JSON.parse(mount.dataset.init)

render(
    <SizeWidget {...data} />,
    mount
)
