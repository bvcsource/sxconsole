// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import 'perfect-scrollbar/jquery'
import mapValues from 'lodash/mapValues'
import React from 'react'
import { render } from 'react-dom'

import VolumeList from './VolumeList'
import UserList from './UserList'
import ClusterStats from './ClusterStats'

{
    const $tabs = $('#cluster-tabs a[data-toggle="tab"]')

    // Load last used tab
    const lastTab = window.localStorage.ClusterTabs || $tabs.attr('href')
    $tabs.filter(`[href="${lastTab}"]`).tab('show')

    // Save last used tab
    $tabs.on('show.bs.tab', (e) => {
        window.localStorage.ClusterTabs = $(e.target).attr('href')
    })
}


{
    const volumeUrls = mapValues(window._volumeUrls, urlTemplate =>
        v => urlTemplate.replace('__volume__', v.name)
    )
    const mount = document.getElementById('cluster-volumes')
    const clusterId = mount.dataset.clusterId
    render(
        <VolumeList clusterId={clusterId} urls={volumeUrls} />,
        mount
    )
}

{
    const userUrls = mapValues(window._userUrls, urlTemplate =>
        u => urlTemplate.replace('__user__', u.email)
    )
    const mount = document.getElementById('cluster-users')
    const clusterId = mount.dataset.clusterId
    const props = {
        clusterId,
        urls: userUrls,
        showLoginOptions: window.showLoginOptions,
    }
    render(
        <UserList {...props} />,
        mount
    )
}

{
    const mount = document.getElementById('cluster-stats')
    const props = JSON.parse(mount.dataset.props)
    render(
        <ClusterStats {...props} />,
        mount
    )

    $(() => {
        const $charts = $('.scrollbar-x-container')
        $charts.perfectScrollbar({
            suppressScrollY: true,
        })
    })
}
