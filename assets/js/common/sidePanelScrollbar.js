// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import 'perfect-scrollbar/jquery'


$(() => {
    const $list = $('.js-cluster-list')
    if ($list.length) {
        $list.perfectScrollbar({
            suppressScrollX: true,
        })
    }
})
