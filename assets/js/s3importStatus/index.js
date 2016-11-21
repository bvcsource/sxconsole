// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'


$(() => {
    setInterval(
        () => $('#refresh').load(`${location.href} #refresh`),
        5000
    )
})
