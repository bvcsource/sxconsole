// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

/** @file Provides global functionalities */
import $ from 'jquery'
import _ from 'lodash'
import 'bootstrap-datepicker'
import 'bootstrap'

import './scrollbars'
import './sidePanelScrollbar'


// Focus the first visible form input on the page (forms, etc)
$('form:not(.js-noautofocus) input:not([type="hidden"])').first().focus()


// Truncate long strings and add tooltips with original text
{
    $.fn.trunc = function trunc() {
        this.find('.js-trunc:visible').each(function truncateText() {
            const $this = $(this)
            const $parent = $this.parent()
            const parentWidth = $parent.width()
            if (parentWidth < 20) {
                // eslint-disable-next-line no-console
                console.warn('Not truncating because of odd width:', parentWidth, $this[0])
                return
            }
            $parent.css('white-space', 'nowrap')

            // Load and save original text
            let text = $this.data('original-text')
            if (!text) {
                text = $this.text()
                $this.data('original-text', text)
            } else {
                $this.text(text)
            }

            const targetWidth = $parent.width() -
                ($this.position().left + Math.max(0, $parent.position().left))
            const ellipsis = "\u2026"
            const left = text.substr(0, text.length/2).split('')
            const right = text.substr(text.length/2).split('')
            let i = 0

            function finished() {
                if ($this.width() <= targetWidth) {
                    return true
                }
                $this.text([left.join(''), right.join('')].join(ellipsis))
                return (_.some([left, right], _.isEmpty))
            }

            // Remove letters from the middle until text is short enough
            while (!finished()) {
                i++
                if (i % 2 === 0) {
                    left.pop()
                } else {
                    right.shift()
                }
            }

            // Add a tooltip with the original text
            if ($this.text() !== text) {
                $this.attr('title', text)
            } else {
                $this.attr('title', null)
            }
        })
    }

    const $body = $('body')

    function reTrunc() {
        $body.trunc()
    }

    // Apply truncation on $(document).ready
    // FIXME apparently it's still too early? maybe this will help...
    setTimeout(reTrunc)

    $(window).on('resize', _.debounce(reTrunc, 100))

    $body.on('shown.bs.tab', (e) => {
        const query = $(e.target).attr('href')
        $(query).trunc()
    })
}


// Language selector
{
    const $form = $('.js-language-select')
    $form.on('click', 'a', function submitLanguageForm() {
        $form.find('input[name=language]').val(this.dataset.lang)
        $form.submit()
    })
}


// Mount datepickers
{
    const defaultConfig = { format: 'yyyy-mm-dd' }
    $('.js-datepicker').each(function mountDatepicker() {
        const $this = $(this)
        let config = $this.data('config') || {}
        config = _.merge({}, defaultConfig, config)
        $this.datepicker(config)
    })
}
