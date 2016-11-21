// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, Component } from 'react'
import { connect } from 'react-redux'

import { getZoneNames } from '../reducers'
import { nodeDndContext } from './dnd'
import AddNodeModal from './AddNodeModal'
import Zone from './Zone'
import SubmitChangesModal from './SubmitChangesModal'
import { AddZoneModal } from './Zone/modals'


const mapStateToProps = state => ({
    zoneNames: getZoneNames(state),
})

@connect(mapStateToProps)
@nodeDndContext
export default class NodeManagement extends Component {
    static propTypes = {
        zoneNames: PropTypes.array.isRequired,
    }

    render() {
        return (
            <div>
                <div className='btn-row'>
                    <SubmitChangesModal />
                    {' '}
                    <AddZoneModal />
                    {' '}
                    <AddNodeModal />
                </div>
                <div children={this.props.zoneNames.map(this.renderZone)} />
            </div>
        )
    }

    renderZone = zoneName => (
        <Zone key={zoneName} zoneName={zoneName} />
    )
}
