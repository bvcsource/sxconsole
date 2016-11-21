// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'
import { render } from 'react-dom'

import ManageAdminClusters from './ManageAdminClusters'


const mount = document.getElementById('manage-clusters')
const clusters = JSON.parse(mount.dataset.clusters)
render(
    <ManageAdminClusters clusters={clusters} />,
    mount
)
