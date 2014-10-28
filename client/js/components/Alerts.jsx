/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');

var Alert = require('./Alert.jsx');

var Alerts = React.createClass({
  propTypes: {
    items: React.PropTypes.arrayOf(
      React.PropTypes.shape({
        id: React.PropTypes.any.isRequired
      })
    ),
    onDismiss: React.PropTypes.func.isRequired
  },

  handleAlertClose(id) {
    this.props.onAlertClose(id);
  },

  render() {
    var alerts = _.map(this.props.items, item =>
      <Alert key={item.id}
        alert={item}
        onClose={_.partial(this.props.onDismiss, item.id)} />
    );

    return (
      <div className="alerts">
        {alerts}
      </div>
    );
  }
});

module.exports = Alerts;
