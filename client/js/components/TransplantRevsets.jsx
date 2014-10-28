/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');
var TransplantRevset = require('./TransplantRevset.jsx');

var TransplantRevsets = React.createClass({
  propTypes: {
    revsets: React.PropTypes.arrayOf(
      React.PropTypes.shape({
        revset: React.PropTypes.string.isRequired
      })
    ),
    onChangeCommit: React.PropTypes.func.isRequired,
    onChangeSquash: React.PropTypes.func.isRequired,
    onChangeSquashedMessage: React.PropTypes.func.isRequired,
    onDelete: React.PropTypes.func.isRequired
  },

  render: function() {
    return (
      <div className="transplantRevsets">
        {this.props.revsets.map(revset =>
          <TransplantRevset key={revset.revset}
            revset={revset}
            onChangeSquash={_.partial(this.props.onChangeSquash, revset.revset)}
            onChangeCommit={_.partial(this.props.onChangeCommit, revset.revset)}
            onChangeSquashedMessage={_.partial(this.props.onChangeSquashedMessage, revset.revset)}
            onDelete={_.partial(this.props.onDelete, revset.revset)} />
        )}
      </div>
    );
  }
});

module.exports = TransplantRevsets;
