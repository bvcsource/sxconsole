// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import { CommonInput } from '../utils/forms'
import SizeInput from '../components/SizeInput'


export class NodeSizeInput extends SizeInput {
    static defaultProps = {
        ...SizeInput.defaultProps,
        label: __("Node size"),
        name: "capacity",
    }
}


const ipInputProps = {
    validations: { matchRegexp: /^(\d{1,3}\.){3}\d{1,3}$/ },
    validationError: __("This is not a valid IP address"),
}

export class IpInput extends CommonInput {
    static defaultProps = _.merge({}, ipInputProps, {
        label: __("Node IP"),
        name: "publicIp",
        required: true,
    })
}

export class InternalIpInput extends CommonInput {
    static defaultProps = _.merge({}, ipInputProps, {
        label: __("Node internal IP"),
        name: "privateIp",
        required: false,
    })
}
