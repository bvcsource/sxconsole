// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import moment from 'moment'
import i18n from 'i18next'


const translations = require('i18next-resource-store-loader!.')
const language = document.documentElement.getAttribute('lang')

moment.locale(language)

i18n.init({
    load: 'currentOnly',
    resources: translations,
    lng: language,
    // No namespaces and keys
    nsSeparator: false,
    keySeparator: false,
    // We expect only non-empty strings:
    returnNull: false,
    returnEmptyString: false,
    returnObjects: false,
})

module.exports = i18n.t.bind(i18n)
