// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { getZoneNames, getZoneNodeIds } from '../reducers'

import Zone from './Zone'
import SubmitChangesModal from './SubmitChangesModal'


function mapStateToProps(state) {
    const zoneNames = getZoneNames(state)
        .filter(
            name => getZoneNodeIds(state, name).length > 0
        )
    return { zoneNames }
}

@connect(mapStateToProps)
export default class MarkFaulty extends PureComponent {
    static propTypes = {
        zoneNames: PropTypes.array.isRequired,
    }

    render() {
        return (
            <div>
                <div className='btn-row'>
                    <SubmitChangesModal />
                </div>
                <div children={this.props.zoneNames.map(this.renderZone)} />
            </div>
        )
    }

    renderZone = name => <Zone zoneName={name} />
}
