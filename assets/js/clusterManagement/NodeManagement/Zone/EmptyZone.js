// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React from 'react'


/**
 * Placeholder rendered inside empty zones.
 * Enables adding nodes back to an empty zone
 */
export default function EmptyZone() {
    const baseClass = 'zones-management__node'
    const nodeClass = `${baseClass} ${baseClass}--placeholder`
    return (
        <div className='col-xs-12'>
            <div
                className={nodeClass}
                children={__("This zone is empty.")}
            />
        </div>
    )
}
