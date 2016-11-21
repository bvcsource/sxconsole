// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import zipObject from 'lodash/zipObject'
/**
 * Creates enums. Given any number of keys, returns a {key: key} object.
 */
export function keyMirror(...keys) {
    return zipObject(keys, keys)
}


/**
 * Simple enum for describing state of a remote resource.
 * @enum {string}
 */
export const ResourceState = keyMirror(
    'LOADING',
    'ERROR',
    'EMPTY',
    'OK',
)

/**
 * Alert types
 * @enum {string}
 */
export const Alert = keyMirror(
    'SUCCESS',
    'INFO',
    'WARNING',
    'DANGER',
)
Alert.ERROR = Alert.DANGER
Alert.WARN = Alert.WARNING
