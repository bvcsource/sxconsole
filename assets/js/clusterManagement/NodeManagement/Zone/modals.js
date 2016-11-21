// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import difference from 'lodash/difference'
import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { getZoneNames } from '../../reducers'
import { addZone, renameZone } from '../../actions'
import FormModalTrigger from '../../../utils/modals/FormModalTrigger'
import { Input } from '../../../utils/forms'


function mapStateToProps(state, ownProps) {
    const zoneNames = getZoneNames(state)
    const safeZoneNames = ['', ownProps.zoneName]
    const reservedNames = difference(zoneNames, safeZoneNames)
    return { reservedNames }
}

class BaseZoneModal extends FormModalTrigger {
    static propTypes = {
        zoneName: PropTypes.string,
        reservedNames: PropTypes.array.isRequired,
    }

    modalClassName = 'modal-dialog modal-sm'
    triggerClassName = 'btn btn-default'

    renderModalBody() {
        return (
            <ZoneNameInput
                inputRef={n => n && n.focus()}
                value={this.props.zoneName}
                reservedNames={this.props.reservedNames}
            />
        )
    }

    onValidSubmit = (rawData) => {
        this.disableSubmit()
        this.performSubmit(rawData)
        this.closeModal()
    }
}

class ZoneNameInput extends PureComponent {
    static propTypes = {
        reservedNames: PropTypes.array.isRequired,
    }

    render() {
        const baseProps = {
            label: __("Zone name"),
            name: 'name',
            required: true,
            validations: {
                matchRegexp: /^[\w -]+$/,
                notIn: this.props.reservedNames,
                maxLength: 128,
            },
            validationErrors: {
                matchRegexp: __("This is not a valid zone name."),
                notIn: __("This zone already exists."),
                maxLength: __("This zone name is too long."),
            },
        }
        return <Input {...baseProps} {...this.props} />
    }
}

@connect(mapStateToProps, { addZone })
export class AddZoneModal extends BaseZoneModal {
    static propTypes = {
        ...BaseZoneModal.propTypes,
        addZone: PropTypes.func.isRequired,
    }

    modalTitle = __("Add zone")
    triggerText = __("Add zone")

    performSubmit(formData) {
        this.props.addZone(formData.name)
    }
}

@connect(mapStateToProps, { renameZone })
export class RenameZoneModal extends BaseZoneModal {
    static propTypes = {
        ...BaseZoneModal.propTypes,
        renameZone: PropTypes.func.isRequired,
    }

    modalTitle = __("Rename zone")
    triggerText = <span className='fa fa-pencil' />
    triggerClassName = 'btn btn-default btn-xs'
    submitText = __("Rename")

    performSubmit(formData) {
        this.props.renameZone(
            this.props.zoneName,
            formData.name
        )
    }
}
