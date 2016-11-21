// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import _ from 'lodash'

import { $stats, addChart, updateGraphs, refreshGraphs, fetchStats } from './core'
import { registerScroll } from './scroll'


const $controls = $('.js-stats-controls')

initStats()

function initStats() {
    const THREE_HOURS = 3 * 60 * 60 * 1000
    const chartNames = {
        space_usage: __("Stored data"),
        loadavg: __("System load average"),
        mem_free: __("Memory free"),
        mem_used: __("Memory used"),
        disk_free: __("Disk free"),
        disk_usage: __("Disk usage"),
        network_in: __("Incoming traffic"),
        network_out: __("Outgoing traffic"),
    }
    fetchStats(THREE_HOURS, null, (stats) => {
        $stats.html('')
        _.each(chartNames, (name, id) => addChart(stats[id], id, name))
    })
}

$controls.find('.js-intervals button').on('click', (e) => {
    // Calculate the delta (e.g. '24 30' = 1 month)
    const delta = e.currentTarget.dataset.delta
        .split(' ')
        .map(n => _.parseInt(n))
        .reduce((l, r) => l * r)
        * 1000 * 60 * 60

    // Load new data
    updateGraphs(delta)
})

registerScroll($('.js-scroll-top'))


{ // Sticky stats controls
    applyAffix($controls)

    function destroyAffix($el) {
        // https://github.com/twbs/bootstrap/issues/5870
        $(window).off('.affix')
        $el
            .removeData('bs.affix')
            .removeClass('affix affix-top affix-bottom')
            .css('width', '')
    }

    function applyAffix($el) {
        const unit = 15
        const offset = $el.offset()
        $el
            .css({
                top: unit,
                left: offset.left,
                zIndex: 1,
                width: $el.outerWidth(),
            })
            .affix({
                offset: {
                    top: offset.top - unit,
                },
            })
    }

    function refreshControlsAffix() {
        destroyAffix($controls)
        applyAffix($controls)
    }

    $(window).on('resize', _.debounce(refreshControlsAffix, 40))
}

// Handler for refresh button
$('.js-refresh').on('click', _.debounce(refreshGraphs, 40))

{ // Handler for auto-refresh button
    let autoRefreshID
    const REFRESH_INTERVAL = 10 * 1000
    function refreshLoop() {
        autoRefreshID = setTimeout(() => {
            refreshGraphs()
            refreshLoop()
        }, REFRESH_INTERVAL)
    }

    $('.js-auto-refresh').on('click', (e) => {
        const btn = {
            $: $(e.currentTarget),
            on: 'btn-success',
            off: 'btn-default',
        }
        const icon = {
            $: btn.$.find('.fa'),
            on: 'fa-pause',
            off: 'fa-play',
        }
        if (btn.$.hasClass(btn.on)) {
            clearTimeout(autoRefreshID)
        } else {
            refreshLoop()
        }
        btn.$.toggleClass(btn.off).toggleClass(btn.on)
        icon.$.toggleClass(icon.off).toggleClass(icon.on)
    })
}
