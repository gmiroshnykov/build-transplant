/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');
var EditableCommit = require('./EditableCommit.jsx');

var SQUASH_SEPARATOR = "\n----------------\n";

var TransplantRevset = React.createClass({
  propTypes: {
    revset: React.PropTypes.shape({
      revset: React.PropTypes.string.isRequired,
      squash: React.PropTypes.bool.isRequired,
      squashedMessage: React.PropTypes.string,
      commits: React.PropTypes.arrayOf(
        React.PropTypes.shape({
          node: React.PropTypes.string.isRequired
        })
      ),
    }),
    onChangeSquash: React.PropTypes.func.isRequired,
    onChangeSquashedMessage: React.PropTypes.func.isRequired
  },

  generateSquashedMessage() {
    return _.pluck(this.props.revset.commits, 'message').join(SQUASH_SEPARATOR);
  },

  handleChangeSquash(e) {
    var flag = e.target.checked;
    this.props.onChangeSquash(flag);
  },

  handleChangeSquashedMessage(e) {
    var squashedMessage = e.target.value;
    this.props.onChangeSquashedMessage(squashedMessage);
  },

  render() {
    var revset = this.props.revset;
    var commitsCount = revset.commits.length;

    return (
      <div className="panel panel-default">
        <div className="panel-heading clearfix">
            <div className="pull-left">
              Revision Set <code>{revset.revset}</code> (commits: {commitsCount})
            </div>
            <div className="form-inline pull-right" role="form">
              {this.renderSquashCheckbox()}
              <button type="button" className="btn btn-danger btn-xs"
                onClick={this.props.onDelete}>delete</button>
            </div>
        </div>
        <div className="list-group">
          {revset.squash ? this.renderSquashedForm() : this.renderCommits()}
        </div>
      </div>
    );
  },

  renderSquashCheckbox() {
    var revset = this.props.revset;
    if (revset.commits.length < 2) {
      return;
    }

    return (
      <div className="checkbox" style={{'padding-right': 15}}>
        <label>
          <input type="checkbox"
            checked={revset.squash}
            onChange={this.handleChangeSquash} /> squash
        </label>
      </div>
    );
  },

  renderSquashedForm() {
    var squashedMessage = this.props.revset.squashedMessage;
    if (squashedMessage === null) {
      squashedMessage = this.generateSquashedMessage();
    }

    return (
      <div className="list-group-item">
        <form role="form">
          <div className="form-group">
            <label>Squashed message</label>
            <textarea className="form-control" rows="5"
              value={squashedMessage}
              onChange={this.handleChangeSquashedMessage} />
          </div>
        </form>
      </div>
    );
  },

  renderCommits() {
    return this.props.revset.commits.map(commit =>
      <div key={commit.node} className="list-group-item">
        <EditableCommit
          commit={commit}
          onChange={_.partial(this.props.onChangeCommit, commit.node)} />
      </div>
    );
  },
});

module.exports = TransplantRevset;
