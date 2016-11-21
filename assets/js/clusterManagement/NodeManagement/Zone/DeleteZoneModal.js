// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import { connect } from 'react-redux'

import SubmittableModal from '../../../utils/modals/SubmittableModal'
import { removeZone } from '../../actions'


const mapDispatchToProps = (dispatch, ownProps) => ({
    onSubmit: () => dispatch(
        removeZone(ownProps.zoneName)
    ),
})
@connect(null, mapDispatchToProps)
export default class DeleteZoneModal extends SubmittableModal {
    static propTypes = {
        zoneName: PropTypes.string.isRequired,
        onSubmit: PropTypes.func.isRequired,
    }

    modalTitle = __("Delete zone?")
    triggerText = <span className='fa fa-times' />
    submitText = __("Delete")
    modalClassName = 'modal-dialog modal-sm'
    triggerClassName = 'btn btn-xs btn-default'

    renderModalBody() {
        return (
            <div
                className='form-group'
                children={__(
                    "Zone {{name}} will be deleted.",
                    { name: this.props.zone })}
            />
        )
    }
}
