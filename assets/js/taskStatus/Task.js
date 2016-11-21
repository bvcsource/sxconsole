// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import moment from 'moment'


export default class Task {
    constructor(data) {
        this.id = data.id
        this.ready = data.ready
        this.status = data.status
        this.info = data.info

        this.type = data.type
        this.displayType = data.type_display

        this.queueDate = moment(data.queue_date)

        this.startDate = (data.start_date)
            ? moment(data.start_date)
            : null

        this.endDate = (data.end_date)
            ? moment(data.end_date)
            : null
    }
}
