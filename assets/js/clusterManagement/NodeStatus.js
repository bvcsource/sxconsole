// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'


export default function NodeStatus({ node }) {
    return <span children={displayNodeStatus(node)} />
}
NodeStatus.propTypes = {
    node: PropTypes.object.isRequired,
}

export function displayNodeStatus(node) {
    if (node.isNew) {
        return __("New node")
    } else if (node.isFaulty) {
        return __("Faulty")
    } else if (node.isDown) {
        return __("Offline")
    }
    return __("Healthy")
}
