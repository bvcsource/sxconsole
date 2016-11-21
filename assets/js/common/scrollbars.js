// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import throttle from 'lodash/throttle'
import 'perfect-scrollbar/jquery'


$(() => {
    $(window).on('resize', throttle(refreshScrollbars, 100))
})

function refreshScrollbars() {
    $('.ps-container').perfectScrollbar('update')
}
