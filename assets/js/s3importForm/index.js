// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'


$(() => {
    const $form = $('.js-form')
    const $adv = $form.find('.js-form-advanced')
    const $option = $form.find('input[name=advanced]')

    $option.on('change', (e) => {
        switch (e.target.checked) {
        case true:
            $adv.removeClass('hidden')
            $adv.find(':input').prop('disabled', false)
            break
        case false:
            $adv.addClass('hidden')
            $adv.find(':input').prop('disabled', true)
            break
        default:
            throw new Error(`Unknown option: ${e.target.value}`)
        }
    })

    /* Apply current option */
    $option.filter('[checked]').change()
})
