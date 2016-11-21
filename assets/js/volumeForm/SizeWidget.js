// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import bytes from 'bytes'
import React from 'react'

import SizeSliderMixin from '../components/SizeSliderMixin'


const SizeWidget = React.createClass({
    mixins: [SizeSliderMixin],
    getDefaultProps() {
        return { defaultValue: bytes('20GB') }
    },
})

export default SizeWidget
