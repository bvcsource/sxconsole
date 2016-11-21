// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { Component } from 'react'

import ManageCluster from './ManageCluster'


export default class ManageAdminClusters extends Component {
    static propTypes = {
        clusters: React.PropTypes.array.isRequired,
    }

    render() {
        return (
            <table className='table table-striped'>
                <thead>
                    <tr>
                        <th children={__("Cluster name")} />
                        <th
                            className='text-right'
                            children={__("Administrator rights")}
                        />
                    </tr>
                </thead>
                <tbody children={this.props.clusters.map(this.renderCluster)} />
            </table>
        )
    }

    renderCluster = c => <ManageCluster key={c.id} cluster={c} />
}
