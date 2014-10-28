var React = require('react');
var TransplantApp = require('./components/TransplantApp.jsx');

React.renderComponent(
  TransplantApp({repositories: REPOSITORIES}),
  document.getElementById('app')
);
