// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'

$(() => {
    const $form = $('.js-form')
    const $inv = $form.find('.js-form-invite')
    const $pass = $form.find('.js-form-password')
    const $option = $form.find('input[name=option]')

    $option.on('change', (e) => {
        switch (e.target.value) {
        case 'invite':
            $inv.removeClass('hidden')
            $pass.addClass('hidden')
            break
        case 'set_password':
            $inv.addClass('hidden')
            $pass.removeClass('hidden')
            break
        default:
            throw new Error(`Unknown option: ${e.target.value}`)
        }
    })

    /* Apply current option */
    $option.filter('[checked]').change()
})
