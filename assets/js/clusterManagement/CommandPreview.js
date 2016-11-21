// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import $ from 'jquery'
import debounce from 'lodash/debounce'
import isEqual from 'lodash/isEqual'
import React, { PropTypes } from 'react'

import { ResourceState } from '../utils/enums'


export default class CommandPreview extends React.Component {
    static propTypes = {
        url: PropTypes.string.isRequired,
        data: PropTypes.object.isRequired,
    }

    state = {
        previewState: ResourceState.LOADING,
        preview: '',
    }

    componentWillMount() {
        this.loadData()
    }

    componentWillReceiveProps(nextProps) {
        if (!isEqual(this.props, nextProps)) {
            this.loadData()
        }
    }

    render() {
        return (
            <div>
                <p>
                    {__("The following command will be executed:")}
                </p>
                {this.renderPreview()}
            </div>
        )
    }

    renderPreview() {
        switch (this.state.previewState) {
        case ResourceState.LOADING:
            return <Loading />
        case ResourceState.ERROR:
            return <Retry onClick={this.loadData} />
        case ResourceState.OK:
            return <pre children={this.state.preview} />
        default:
            throw new Error(
                `CommandPreview doesn't support this state: ${this.state.previewState}`)
        }
    }

    loadData = debounce(() => {
        this.setState({ previewState: ResourceState.LOADING })

        const success = data => this.setState({
            previewState: ResourceState.OK,
            preview: data.args,
        })

        const error = () => this.setState({
            previewState: ResourceState.ERROR,
        })

        $.ajax({
            method: 'get',
            url: this.props.url,
            data: this.props.data,
            success,
            error,
        })
    }, 300)
}

const Loading = () => (
    <p className='text-muted'>
        {__("Loading...")}
    </p>
)

const Retry = ({ onClick }) => (
    <p>
        <span className='text-muted'>
            {__("Failed to load preview.")}
        </span>
        &nbsp;
        <button
            className='btn btn-link'
            onClick={onClick}
            children={__("Retry")}
        />
    </p>
)
Retry.propTypes = {
    onClick: PropTypes.func.isRequired,
}
