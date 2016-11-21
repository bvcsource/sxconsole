// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, Component } from 'react'
import { connect } from 'react-redux'

import { restoreNode } from '../../actions'


@connect(null, { restoreNode })
export default class RestoreNodeButton extends Component {
    static propTypes = {
        restoreNode: PropTypes.func.isRequired,
        nodeId: PropTypes.string.isRequired,
    }

    render() {
        return (
            <button className='btn btn-default btn-xs' onClick={this.restoreNode}>
                <span className='fa fa-undo' />
            </button>
        )
    }

    restoreNode = () => this.props.restoreNode(this.props.nodeId)
}
