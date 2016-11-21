// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, PureComponent } from 'react'
import { connect } from 'react-redux'

import { unmarkFaultyNode } from '../actions'


@connect(null, { unmarkFaultyNode })
export default class UnmarkFaultyNodeButton extends PureComponent {
    static propTypes = {
        unmarkFaultyNode: PropTypes.func.isRequired,
        nodeId: PropTypes.string.isRequired,
        disabled: PropTypes.bool,
    }

    render() {
        return (
            <button
                className='btn btn-default btn-xs'
                disabled={this.props.disabled}
                onClick={this.unmarkFaultyNode}
                children={
                    <span className='fa fa-undo' />
                }
            />
        )
    }

    unmarkFaultyNode = () => this.props.unmarkFaultyNode(this.props.nodeId)
}
