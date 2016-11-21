#!/usr/bin/env node
// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

/**
 * @file Manages translations for javascript files.
 */

const path = require('path')
const fs = require('fs')

const conv = require('i18next-conv')
const i18nExtract = require('i18n-extract')


const commands = {
    collect: 'collect',
    process: 'process',
}
const command = process.argv[2]
const languages = ['en', 'de', 'it', 'pl']
function translationFilePath(lang) {
    return path.join(
        __dirname,
        'sx-translations/sxconsole',
        lang,
        'LC_MESSAGES/javascript.po'
    )
}
const jsonDir = path.join(__dirname, 'assets/i18n/')
function jsonFilePath(lang) {
    return path.join(
        __dirname,
        'assets/i18n/',
        lang,
        'translation.json'
    )
}

if (command === commands.collect) {
    collectMessages()
} else if (command === commands.process) {
    processMessages()
} else {
    showHelp()
}

function collectMessages() {
    const jsFiles = path.join(__dirname, 'assets/js/**/*.js')
    const messages = i18nExtract.extractFromFiles(jsFiles, { marker: '__' })

    languages.forEach((lang) => {
        const out = translationFilePath(lang)
        i18nExtract.mergeMessagesWithPO(messages, out, out)
    })
}

function processMessages() {
    if (!fs.existsSync(jsonDir)) {
        console.log(`Creating missing directory: ${jsonDir}`) // eslint-disable-line no-console
        fs.mkdirSync(jsonDir)
    }

    languages.forEach((lang) => {
        const source = translationFilePath(lang)
        const target = jsonFilePath(lang)
        conv.gettextToI18next(lang, source, target)
    })
}

function showHelp() {
    const name = path.basename(process.argv[1])
    /* eslint-disable no-console */
    console.log(
`Usage: ./${name} <command>

Manages translations for javascript files.

Commands:
    ${commands.collect}\tUpdate translation files with current strings.
    ${commands.process}\tConvert translation files to json.`
    )
    process.exit(2)
    /* eslint-enable no-console */
}
