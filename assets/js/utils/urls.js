// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

const urls = {
    volumes(cluster, volume) {
        let url = `/api/v1/clusters/${cluster}/volumes/`
        if (volume) {
            url += `${volume}/`
        }
        return url
    },
    volumeAcl(cluster, volume, user) {
        let url = urls.volumes(cluster, volume)
        url += 'acl/'
        if (user) {
            url += `${user}/`
        }
        return url
    },
    users(cluster, user) {
        let url = `/api/v1/clusters/${cluster}/users/`
        if (user) {
            url += `${user}/`
        }
        return url
    },
    task: uuid => `/api/v1/tasks/${uuid}/`,
    static: path => `/static/${path}`,
}

export default urls
