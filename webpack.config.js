// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

const glob = require('glob')
const path = require('path')
const fs = require('fs')

const get = require('lodash/get')
const webpack = require('webpack')
const ExtractTextPlugin = require('extract-text-webpack-plugin')
const yaml = require('js-yaml')
const mergeDirs = require('merge-dirs')


/* Load and process the conf */
const conf = {}
try {
    Object.assign(conf,
        yaml.safeLoad(fs.readFileSync('./conf.yaml'))
    )
} catch (e) {
    console.warn('Failed to load config file') // eslint-disable-line no-console
}

const debug = Boolean(get(conf, 'server.debug'))
const skinName = conf.skin || 'default'

/** Copy over the skin's images */
const skinImgPath = path.join('skins', skinName, 'img')
if (fs.existsSync(skinImgPath)) {
    mergeDirs(skinImgPath, 'assets/img', /* overwriteExistingFiles= */ true)
}

const skinVarsPath = path.join('skins', skinName, 'sass.json')


module.exports = {
    context: `${__dirname}/assets`,

    entry: {
        /* Page-related js is added dynamically below */
        css: ['./scss/styles.scss'],
    },
    output: {
        path: `${__dirname}/assets/build/`,
        filename: '[name].js',
    },
    plugins: [
        new webpack.DefinePlugin({
            "process.env.NODE_ENV":
                (debug) ? '"dev"' : '"production"',
        }),
        new webpack.ProvidePlugin({
            __: `${__dirname}/assets/i18n`,
            jQuery: 'jquery', /* for bootstrap */
            'window.jQuery': 'jquery', /* for highstock */
        }),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.CommonsChunkPlugin({
            name: '_init',
            minChunks: 2,
        }),
        new ExtractTextPlugin('styles.css'),
    ],
    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: 'babel',
            },
            {
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract(
                    'style-loader',
                    `css!sass!jsontosass?path=${skinVarsPath}`
                ),
            },
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: "url-loader?limit=10000&minetype=application/font-woff",
            },
            {
                test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                loader: "file-loader",
            },
        ],
    },
}

glob.sync(`${__dirname}/assets/js/*/index.js`).forEach((filePath) => {
    const parts = path.dirname(filePath).split('/')
    const id = parts[parts.length - 1]
    module.exports.entry[id] = filePath
})
