// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import { render } from 'react-dom'

import VolumeUsers from './VolumeUsers'


const mount = document.getElementById('volume-users')
const data = JSON.parse(mount.dataset.init)
render(
    <VolumeUsers {...data} />,
    mount
)
