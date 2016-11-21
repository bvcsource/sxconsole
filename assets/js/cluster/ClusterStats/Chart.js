// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import { PieChart, Pie } from 'recharts'


export default function Chart({ value, limit, size }) {
    return (
        <div className={getChartClassName(value, limit)}>
            <PieChart width={size} height={size}>
                <Pie
                    data={getChartData(value, limit)}
                    outerRadius={size / 2}
                    innerRadius={size / 3}
                    startAngle={90}
                    endAngle={-270}
                />
            </PieChart>
        </div>
    )
}
Chart.propTypes = {
    value: PropTypes.number.isRequired,
    limit: PropTypes.number.isRequired,
    size: PropTypes.number,
}
Chart.defaultProps = {
    size: 82,
}

function getChartClassName(value, limit) {
    const className = 'page-stats__chart'
    if (value >= limit) {
        return `${className} ${className}--danger`
    } else if (value / limit > 0.9) {
        return `${className} ${className}--warning`
    }
    return className
}

function getChartData(value, limit) {
    if (value < limit) {
        // display the value vs remaining space
        return buildChartData(value, limit - value)
    }
    // display surplus value vs the limit
    return buildChartData(value - limit, limit)
}

function buildChartData(...values) {
    return values.map(value => ({ value }))
}
