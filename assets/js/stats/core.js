// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import _ from 'lodash'
import c3 from 'c3'

import defaultChartOptions from './defaultChartOptions'
import { getFormatOptions } from './formatters'
import { registerScroll } from './scroll'


const _charts = {}


export const $stats = $('#stats')
export const statsUrl = $stats.data('url')
const $statList = $('.js-stat-list')

export function fetchStats(from, till, cb) {
    if (!till) {
        // Delta shorthand
        const delta = from
        const now = new Date().getTime()
        from = now - delta
        till = now
    }

    const url = `${statsUrl}?from=${from}&till=${till}`
    $.getJSON(url, cb)
}

// Mount and create a new chart
export function addChart(columns, id, label) {
    const $elem = $('<div />', { id, class: 'stats__chart' })
    $elem.appendTo($stats)

    const $chartTitle = $('<h4 />', { class: 'stats__header', text: label })
    const $chart = $('<div />')
    $elem.append($chartTitle)
    $elem.append($chart)

    const $chartLink = $('<a />', { href: `#${id}`, class: 'list-group-item', text: label })
    $statList.append($chartLink)
    registerScroll($chartLink)

    const options = {
        bindto: $chart[0],
        data: { columns },
        zoom: {
            onzoomend: _.debounce((range) => {
                updateGraphs(range[0].getTime(), range[1].getTime())
            }, 200),
        },
    }
    const chart = makeChart(id, options)
    _charts[id] = chart
}


function makeChart(id, options) {
    const formatOptions = getFormatOptions(id)
    options = _.merge({}, defaultChartOptions, formatOptions, options)
    const chart = c3.generate(options)

    // Stack all chart series
    chart.groups([_.map(chart.data(), 'id')])

    const timeline = options.data.columns[0]
    zoomChart(chart, timeline)

    return chart
}

export function updateGraphs(from, till) {
    fetchStats(from, till, (stats) => {
        _.each(stats, (columns, id) => setTimeout(() => updateGraph(columns, id)))
    })
}

function updateGraph(columns, id) {
    const timeline = columns[0]
    const chart = _charts[id]
    if (_.isUndefined(chart)) {
        throw new Error(`No such chart: ${id}.`)
    }

    chart.load({
        columns,
        done: () => zoomChart(chart, timeline),
    })
}


function zoomChart(chart, timeline) {
    const [left, right] = [timeline[1], _.last(timeline)]
    const d = right - left
    const now = new Date().getTime()

    // Expand chart range to enable dragging, then zoom back to the original range
    chart.axis.range({
        min: { x: left - d },
        max: { x: Math.min(right + d, now) },
    })
    chart.zoom([left, right])
}

export function refreshGraphs() {
    const zoom = _.values(_charts)[0].zoom()
    const delta = zoom[1].getTime() - zoom[0].getTime()
    updateGraphs(delta)
}
