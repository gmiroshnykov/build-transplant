/**
 * @jsx React.DOM
 */

var React = require('react');

var UNKNOWN = '<unknown>';

var EditableCommit = React.createClass({
  propTypes: {
    commit: React.PropTypes.shape({
      node: React.PropTypes.string.isRequired,
      author: React.PropTypes.string.isRequired,
      author_email: React.PropTypes.string.isRequired,
      date: React.PropTypes.renderable.isRequired,
      message: React.PropTypes.renderable.isRequired
    })
  },

  handleChangeMessage(e) {
    var message = e.target.value;
    var commit = this.props.commit;
    commit.message = message;
    this.props.onChange(commit);
  },

  render() {
    var commit = this.props.commit;
    var author = [commit.author];
    if (commit.author_email) {
      author.push('<' + commit.author_email + '>');
    }
    author = author.join(' ');

    if (!author) {
      author = UNKNOWN;
    }

    var date = commit.date;
    if (!date) {
      date = UNKNOWN;
    }

    return (
      <form role="form-horizontal">
        <div className="form-group">
          {this.renderLabel('ID')}
          {this.renderStatic(<code>{commit.node}</code>)}
        </div>
        <div className="form-group">
          {this.renderLabel('Author')}
          {this.renderStatic(author)}
        </div>
        <div className="form-group">
          {this.renderLabel('Date')}
          {this.renderStatic(date)}
        </div>
        <div className="form-group clearfix">
          {this.renderLabel('Message')}
          <div className="col-sm-11">
            <textarea className="form-control" rows="5"
              value={this.props.commit.message}
              onChange={this.handleChangeMessage} />
          </div>
        </div>
      </form>
    );
  },

  renderLabel(text) {
    return <label className="control-label col-sm-1">{text}</label>;
  },

  renderStatic(text) {
    return <p className="form-control-static col-sm-11">{text}</p>;
  }
});

module.exports = EditableCommit;
