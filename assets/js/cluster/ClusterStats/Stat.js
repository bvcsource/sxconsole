// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import identity from 'lodash/identity'
import React, { PropTypes } from 'react'

import Chart from './Chart'


export default function Stat({ title, value, limit, display }) {
    return (
        <div className='page-stats__stat'>
            <div>
                <div className='font-large'>
                    {title}
                </div>
                <div
                    className='text-muted'
                    children={(limit)
                        ? __("{{value}} of {{limit}}", {
                            value: display(value),
                            limit: display(limit),
                        })
                        : __("Unlimited")
                    }
                />
            </div>
            {(limit)
                ? <Chart value={value} limit={limit} />
                : <div className='page-stats__stat-text' children={display(value)} />
            }
        </div>
    )
}
Stat.propTypes = {
    title: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    limit: PropTypes.number,
    display: PropTypes.func,
}
Stat.defaultProps = {
    display: identity,
}
