/**
 * @jsx React.DOM
 */

var React = require('react');

var Alert = React.createClass({
  propTypes: {
    alert: React.PropTypes.shape({
      id: React.PropTypes.string.isRequired,
      type: React.PropTypes.string.isRequired,
      message: React.PropTypes.renderable.isRequired,
      dismissable: React.PropTypes.bool
    })
  },

  render() {
    var alert = this.props.alert;
    var type = alert.type || 'info';
    var dismissable = alert.dismissable || false;


    var classes = ['alert'];
    classes.push('alert-' + type);

    if (dismissable) {
      classes.push('alert-dismissible');
    }

    return (
      <div role="alert" className={classes.join(' ')}>
        <button type="button" className="close"
          onClick={this.props.onClose}><span aria-hidden="true">&times;</span><span className="sr-only">Close</span></button>
        {alert.message}
      </div>
    );
  }
});

module.exports = Alert;
