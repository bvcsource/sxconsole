// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import bytes from 'bytes'
import moment from 'moment'


const SPEED_CHARTS = new Set(['network_in', 'network_out'])
const FLOAT_CHARTS = new Set(['loadavg'])

export function getFormatOptions(chartId) {
    const options = _.merge(
        {},
        getYTickFormat(chartId),
        getXTickFormat(chartId),
        getTooltipTitleFormat(chartId),
    )
    return options
}

function getXTickFormat() {
    return _.set({}, 'axis.x.tick.format', dateFormat)
}

function getYTickFormat(chartId) {
    let formatter
    if (SPEED_CHARTS.has(chartId)) {
        formatter = speedFormat
    } else if (FLOAT_CHARTS.has(chartId)) {
        formatter = floatFormat
    } else {
        formatter = bytes
    }
    return _.set({}, 'axis.y.tick.format', formatter)
}

function getTooltipTitleFormat() {
    return _.set({}, 'tooltip.format.title', tooltipFormat)
}

function speedFormat(value) {
    // Convert bytes into bits per second
    value *= 8
    value = bytes(value)
    value = value.replace(/B$/, "b/s")
    return value
}

function floatFormat(num) {
    return _.round(num, 2)
}

function dateFormat(date) {
    date = moment(date)
    const z = this.api.zoom()
    const delta = z[1].getTime() - z[0].getTime()
    const day = 24 * 60 * 60 * 1000
    const year = 365 * day

    let label
    if (delta < 2 * day) {
        label = date.format('HH:mm')
    } else if (delta < year) {
        label = date.format('D MMM')
    } else {
        label = date.format('MM.YYYY')
    }
    return label
}

function tooltipFormat(date) {
    return moment(date).format('YYYY-MM-DD HH:mm')
}
