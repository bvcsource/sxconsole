// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, Component } from 'react'
import { connect } from 'react-redux'

import { removeNode } from '../../actions'


@connect(null, { removeNode })
export default class RemoveNodeButton extends Component {
    static propTypes = {
        removeNode: PropTypes.func.isRequired,
        nodeId: PropTypes.string.isRequired,
    }

    render() {
        return (
            <button className='btn btn-default btn-xs' onClick={this.removeNode}>
                <span className='fa fa-times' />
            </button>
        )
    }

    removeNode = () => this.props.removeNode(this.props.nodeId)
}
