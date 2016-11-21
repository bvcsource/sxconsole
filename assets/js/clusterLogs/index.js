// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import React from 'react'
import { render } from 'react-dom'

import { ajax } from '../utils/ajax'
import AccessLogLoader from './AccessLogLoader'


$(() => {
    const $form = $('.js-filter-form')

    $form.on('submit', (e) => {
        e.preventDefault()
        ajax({
            method: 'post',
            url: $form.prop('action'),
            data: $form.serialize(),
            success(data) {
                const mountNode = document.getElementById('access-log-content')
                render(
                    <AccessLogLoader taskId={data.task_id} />,
                    mountNode
                )
            },
        })
    })
})
