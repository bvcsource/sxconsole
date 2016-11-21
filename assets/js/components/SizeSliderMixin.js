// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes } from 'react'
import isInteger from 'lodash/isInteger'

import bytes from '../utils/bytes'


// Displays a slider widget for entering a size (e.g. volume size)
export default {
    propTypes: {
        minValue: PropTypes.number.isRequired,
        maxValue: PropTypes.number.isRequired,
        value: PropTypes.number,
        defaultValue: PropTypes.number,
    },

    getInitialState() {
        const value = this.props.value ||
            this.validateSize(this.props.defaultValue)
        return {
            value,
            displayValue: bytes(value),
        }
    },

    render() {
        return (
            <div className='row'>
                <div className='col-xs-9'>
                    <input
                        className='form-control'
                        type='range'
                        min={this.props.minValue}
                        max={this.props.maxValue}
                        value={this.state.value}
                        onChange={this.sliderMoved}
                    />
                </div>
                <div className='col-xs-3'>
                    <input
                        className='form-control'
                        type='text'
                        name='size'
                        value={this.state.displayValue}
                        onChange={this.sizeEntered}
                        onBlur={this.sizeSet}
                    />
                </div>
            </div>)
    },

    sliderMoved(e) {
        // When user moves the slider, update value and displayed value
        let value = parseInt(e.target.value, 10)
        if (!isNaN(value)) {
            const displayValue = this.sliderValueToDisplayValue(value)
            value = bytes(displayValue)
            this.setState({ value, displayValue })
        }
    },
    sizeEntered(e) {
        const displayValue = e.target.value
        this.setState({ displayValue })
    },

    sizeSet() {
        let value = bytes(this.state.displayValue)
        if (value) {
            value = this.cleanValue(value)
            this.setState({
                value,
                displayValue: bytes(value),
            })
        } else {
            this.setState({
                displayValue: bytes(this.state.value),
            })
        }
    },

    validateSize(size) {
        size = Math.max(this.props.minValue, size) // Size too small
        size = Math.min(this.props.maxValue, size) // Size too big
        return size
    },

    sliderValueToDisplayValue(value) {
        // Process `bytes` output to round the value
        const numAndUnit = bytes(value, { unitSeparator: ' ' }).split(' ')
        const unit = numAndUnit[1]
        let num = numAndUnit[0]
        num = parseFloat(num)
        num = adaptiveRound(num)
        return this.cleanDisplayValue(`${num}${unit}`)
    },

    cleanValue(value) {
        if (value > this.props.maxValue) {
            value = this.props.maxValue
        } else if (value < this.props.minValue) {
            value = this.props.minValue
        }
        return value
    },

    cleanDisplayValue(displayValue) {
        const value = bytes(displayValue)
        return bytes(this.cleanValue(value))
    },
}

function adaptiveRound(num) {
    let factor
    if (num > 500) {
        factor = 25
    } else if (num > 100) {
        factor = 10
    } else if (num > 25) {
        factor = 5
    } else if (num > 10) {
        factor = 1
    } else if (num > 5) {
        factor = 0.5
    } else if (num > 2.5) {
        factor = 0.25
    } else {
        factor = 0.10
    }
    num = Math.round(num / factor) * factor
    if (!isInteger(num)) {
        num = num.toFixed(2)
    }
    return num
}
