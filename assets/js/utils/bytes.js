// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import endsWith from 'lodash/endsWith'
import isString from 'lodash/isString'


// Wrapper around `bytes` that accepts values in '1G' format
export default function customBytes(value, options) {
    if (shouldAppendUnit(value)) {
        value += 'B'
    }
    return bytes(value, options)
}

function shouldAppendUnit(value) {
    return isString(value) && !endsWith(
        value.toUpperCase(),
        'B'
    )
}
