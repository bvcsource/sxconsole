// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { markNodeAsFaulty } from '../actions'


@connect(null, { markNodeAsFaulty })
export default class MarkNodeAsFaultyButton extends PureComponent {
    static propTypes = {
        markNodeAsFaulty: PropTypes.func.isRequired,
        nodeId: PropTypes.string.isRequired,
        disabled: PropTypes.bool,
    }

    render() {
        return (
            <button
                className='btn btn-default btn-xs'
                disabled={this.props.disabled}
                onClick={this.markNodeAsFaulty}
                children={
                    <span className='fa fa-trash' />
                }
            />
        )
    }

    markNodeAsFaulty = () => this.props.markNodeAsFaulty(this.props.nodeId)
}
