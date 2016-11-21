// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'

const headingClassName = 'zones-management__zone-heading'


export default function ZoneHeading({ zoneName, children }) {
    if (zoneName === '') {
        return (
            <div className={headingClassName}>
                <span
                    className='text-muted'
                    children={__("(zoneless)")}
                />
            </div>
        )
    }
    return (
        <div
            className={headingClassName}
            children={
                [zoneName, ' ', children]
            }
        />
    )
}
ZoneHeading.propTypes = {
    zoneName: PropTypes.string.isRequired,
    children: PropTypes.node,
}
