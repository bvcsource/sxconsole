// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import set from 'lodash/set'
import merge from 'lodash/merge'
import cookies from 'browser-cookies'


export function ajax(options) {
    const addons = {}
    set(addons, 'headers.X-CSRFToken', getCsrfToken())
    merge(options, addons)
    return $.ajax(options)
}

export function getCsrfToken() {
    return cookies.get('csrftoken')
}
