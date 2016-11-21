// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import _ from 'lodash'
import React from 'react'

import { Alert, ResourceState } from '../utils/enums'
import MultiDeleteModal, { DELETE_STATES } from './MultiDeleteModal'


export default class DeleteVolumesModal extends MultiDeleteModal {
    modalTitle = __("Delete volumes?")
    triggerText = __("Delete selected volumes")

    renderMsg() {
        switch (this.state.state) {
        case DELETE_STATES.SUCCESS:
            return null
        case DELETE_STATES.ERROR:
            return __("The following volumes have not been deleted:")
        default:
            return __("The following volumes will be deleted:")
        }
    }

    updateStatus(requests) {
        const states = _.groupBy(requests)

        let iconClass
        let alertType
        let msg
        if (_.has(states, ResourceState.LOADING)) {
            iconClass = 'fa fa-spinner fa-pulse'
            alertType = Alert.INFO
            const all = _.size(requests)
            const done = all - _.size(states[ResourceState.LOADING])
            msg = __("({{done}}/{{all}}) Deleting volumes...", { done, all })
            this.setState({ state: DELETE_STATES.IN_PROGRESS })
        } else if (_.has(states, ResourceState.ERROR)) {
            iconClass = 'fa fa-times'
            alertType = Alert.ERROR
            msg = __("Failed to delete some volumes.")
            this.setState({ state: DELETE_STATES.ERROR })
        } else if (_.isEqual(_.keys(states), [ResourceState.OK])) {
            iconClass = 'fa fa-check'
            alertType = Alert.SUCCESS
            msg = __("Selected volumes have been deleted.")
            this.setState({ state: DELETE_STATES.SUCCESS })
        }
        const alert = (
            <span>
                <span className={iconClass} />
                {' '}
                {msg}
            </span>
        )
        this.setAlert(alertType, alert)
    }
}
