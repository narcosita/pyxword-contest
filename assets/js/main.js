/*
 * Main Javascript file for pyxword_contest.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require('jquery');
require('lodash');
require('font-awesome-webpack');
require('bootstrap');

// App scripts
require('./crossword.js');
require('./halloffame.js');

window.$ = $; // expose jquery
