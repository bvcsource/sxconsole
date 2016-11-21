// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'


$(() => {
    const $replicas = $('#id_replicas')
    const $replicasGroup = $replicas.closest('.form-group')
    const $warning = $('<span class="help-block hidden"></span>')

    $warning.text(__(
        "If one node of the cluster dies, " +
            "the data stored in this volume will become unavailable. " +
            "Recommended value: 2 or greater."))

    $replicas
        .after($warning)
        .on('input', (e) => {
            const value = parseInt(e.target.value, 10)
            if (value < 2) {
                $replicasGroup.addClass('has-warning')
                $warning.removeClass('hidden')
            } else {
                $replicasGroup.removeClass('has-warning')
                $warning.addClass('hidden')
            }
        })
})
