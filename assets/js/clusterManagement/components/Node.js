// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import React, { PropTypes, PureComponent } from 'react'


export default class Node extends PureComponent {
    static propTypes = {
        classModifiers: PropTypes.array,
    }
    static defaultProps = {
        classModifiers: [],
    }

    render() {
        const { classModifiers, ...elementProps } = this.props
        return (
            <div
                className={getClassName(classModifiers)}
                {...elementProps}
            />
        )
    }
}

function getClassName(modifiers) {
    const baseClass = 'zones-management__node'
    const classNames = [
        baseClass,
        ...modifiers.map(mod => `${baseClass}--${mod}`),
    ]
    return classNames.join(' ')
}
