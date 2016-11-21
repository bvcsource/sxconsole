// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'


export function registerScroll($el) {
    $el.on('click', (e) => {
        const targetId = $.attr(e.currentTarget, 'href')
        const $target = $(targetId)
        const scrollTop = ($target.length)
            ? $target.offset().top
            : 0
        $('html, body').animate({ scrollTop }, 250)
        e.preventDefault()
    })
}

