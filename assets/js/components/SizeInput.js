// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import { CommonInput } from '../utils/forms'


export default class SizeInput extends CommonInput {
    static defaultProps = {
        required: true,
        validations: { matchRegexp: /^\d+(\.\d+)?([kmgt]i?)?b?$/i },
        validationError: __("This is not a valid size"),
    }
}
