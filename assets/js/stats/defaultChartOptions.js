// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

export default {
    transition: {
        duration: 0,
    },
    data: {
        order: (l, r) => l.id > r.id,
        type: 'area',
        x: 'x',
    },
    axis: {
        x: {
            type: 'timeseries',
            tick: {
                count: 15,
                multiline: true,
            },
        },
    },
    point: {
        show: false,
    },
    zoom: {
        enabled: true,
    },
}
