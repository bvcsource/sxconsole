// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import React, { PropTypes } from 'react'

import Stat from './Stat'


export default function ClusterStats({ users, volumes, allocatedSpace, spaceUsage }) {
    return (
        <div className='page-stats'>
            <Stat
                title={__("Users")}
                {...users}
            />
            <Stat
                title={__("Volumes")}
                {...volumes}
            />
            <Stat
                title={__("Allocated space")}
                display={bytes}
                {...allocatedSpace}
            />
            <Stat
                title={__("Space usage")}
                display={bytes}
                {...spaceUsage}
            />
        </div>
    )
}
const chartsStatType = PropTypes.shape({
    value: PropTypes.number.isRequired,
    limit: PropTypes.number,
})
ClusterStats.propTypes = {
    users: chartsStatType,
    volumes: chartsStatType,
    allocatedSpace: chartsStatType,
    spaceUsage: chartsStatType,
}
