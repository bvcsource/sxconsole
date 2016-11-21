// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'

import { RenameZoneModal } from './modals'
import DeleteZoneModal from './DeleteZoneModal'
import ZoneHeadingComponent from '../../components/ZoneHeading'


export default function ZoneHeading({ zoneName }) {
    return (
        <ZoneHeadingComponent zoneName={zoneName}>
            <RenameZoneModal zoneName={zoneName} />
            {' '}
            <DeleteZoneModal zoneName={zoneName} />
        </ZoneHeadingComponent>
    )
}
ZoneHeading.propTypes = {
    zoneName: PropTypes.string.isRequired,
}
