// Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
// License: MIT, see LICENSE for more details.

import mapValues from 'lodash/mapValues'
import { ResourceState } from './enums'


/**
 * @mixin
 * @summary Makes it easy to manage statuses for multiple dependent resources
 *
 * To use it, you have to provide following attributes in your class:
 * @param {Object} resources an enum of resource names
 * @example
 * resources: keyMirror('foos', 'bars'),
 *
 * @param {function} loadData method for loading the resources
 * @example
 * loadData() {
 *     this.loadFoos();
 *     this.loadBars();
 * }
 *
 * You can use setResourceState method like this:
 * @example
 * function success(data) {
 *     // New state will include `fooList`
 *     this.setResourceState(this.resources.foos,
 *                           ResourceState.OK,
 *                           {fooList: data.foos});
 * }
 *
 * You could also create a setter with _.partial
 * @example
 * loadFoos() {
 *     let setFoosState = _.partial(this.setResourceState, this.recources.foos);
 *     function success(data) {
 *         if (_.isEmpty(data.foos)
 *             setFoosState(ResourceState.EMPTY);
 *         else
 *             setFoosState(ResourceState.OK);
 *     }
 *     function fail(data) {
 *         setFoosState(ResourceState.ERROR);
 *     }
 * }
 *
 * Now you can use this.state._resourceStates to interprete state in render()
 * method
 * @example
 * render() {
 *     let states = this.state._resourceStates;
 *     if (states.foos == ResourceState.EMPTY)
 *         return this.renderEmpty();
 *     if (_.includes(states, ResourceState.LOADING))
 *         return this.renderLoading();
 *     ...
 *     return this.renderFoos();
 * }
 */
export const AjaxMixin = {
    getInitialState() {
        return {
            _resourceStates: mapValues(
                this.resources,
                () => ResourceState.LOADING
            ),
        }
    },
    componentWillMount() {
        if (this.loadData) {
            this.loadData()
        } else {
            throw new Error(
                "You must implement `loadData` function to use this mixin!")
        }
    },

    /**
     * Set the state of a resource.
     * @param {string} resName Resource name.
     * @param {string} resState State of the resource.
     * @param {Object} [reactState] Extra state to be updated.
     */
    setResourceState(resName, resState, reactState) {
        reactState = reactState || {}
        this.setState({
            ...reactState,
            _resourceStates: {
                ...this.state._resourceStates,
                [resName]: resState,
            },
        })
    },
}
