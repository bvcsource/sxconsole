// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import includes from 'lodash/includes'
import React, { PropTypes, Component } from 'react'

import Formsy, { Decorator as formsyInput } from 'formsy-react'


@formsyInput()
export class Input extends Component {
    static propTypes = {
        label: PropTypes.string,
        name: PropTypes.string.isRequired,
        autoComplete: PropTypes.oneOf(['on', 'off']),
        autoFocus: PropTypes.bool,
        inputRef: PropTypes.func,
        className: PropTypes.string,
        type: PropTypes.string,

        // obtained from Formsy.Decorator
        showError: PropTypes.func,
        isRequired: PropTypes.func,
        getValue: PropTypes.func,
        getErrorMessage: PropTypes.func,
        setValue: PropTypes.func,

        /* eslint-disable react/no-unused-prop-types */
        // These are consumed by Formsy.Decorator:
        value: PropTypes.string,
        required: PropTypes.bool,
        validations: PropTypes.object,
        /* eslint-enable react/no-unused-prop-types */
    }

    static defaultProps = {
        required: true,
        autoComplete: 'off',
        validationErrors: {},
    }

    render() {
        if (this.props.type === 'hidden') {
            return this.renderHiddenField()
        }
        return this.renderCommonField()
    }

    renderHiddenField() {
        return this.renderInput()
    }

    renderCommonField() {
        let className = 'form-group '
        if (this.props.showError()) {
            className += 'has-error '
        }
        if (this.props.className) {
            className += this.props.className
        }
        return (
            <div className={className}>
                {this.renderLabel()}
                {this.renderInput()}
                {this.renderErrorMessage()}
            </div>
        )
    }

    renderLabel() {
        const optionalTip = (
            <span className='label-tip'>
                {' '}
                {__("(optional)")}
            </span>
        )
        return (
            <label className='control-label' htmlFor={this.props.name}>
                {this.props.label}
                {this.props.isRequired() ? null : optionalTip}
            </label>
        )
    }

    renderInput() {
        const props = {
            className: 'form-control',
            type: this.props.type || 'text',
            name: this.props.name,
            onChange: this.changeValue,
            value: this.props.getValue() || '',
            autoComplete: this.props.autoComplete,
            autoFocus: this.props.autoFocus,
            ref: this.props.inputRef,
        }
        return <input {...props} />
    }

    renderErrorMessage() {
        return (
            <span
                className='help-block'
                children={this.props.getErrorMessage()}
            />
        )
    }

    changeValue = e => this.props.setValue(e.target.value)

}

// Class for building common fields.
// Usage: extend CommonInput and provide defaultProps in your class.
export class CommonInput extends Component { // eslint-disable-line react/prefer-stateless-function
    render() {
        return <Input {...this.props} />
    }
}

Formsy.addValidationRule('notIn', (values, value, array) => !includes(array, value))
