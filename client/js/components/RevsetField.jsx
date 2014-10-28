/**
 * @jsx React.DOM
 */

var React = require('react')

var RevsetField = React.createClass({
  propTypes: {
    canAdd: React.PropTypes.bool.isRequired,
    inProgress: React.PropTypes.bool.isRequired,
    onAdd: React.PropTypes.func.isRequired
  },

  getInitialState() {
    return {
      value: ''
    };
  },

  handleKeyDown(e) {
    if (e.keyCode === 13) {
      e.preventDefault();
      this.handleAdd();
    }
  },

  handleChange(e) {
    var value = e.target.value;
    this.setState({value: value});
  },

  handleAdd() {
    if (this.state.value === '') {
      return;
    }

    this.props.onAdd(this.state.value.trim());
  },

  reset() {
    this.setState({value: ''});
    var node = this.refs.revset.getDOMNode();
    node.focus();
  },

  render() {
    var canAdd = this.props.canAdd;
    var inProgress = this.props.inProgress;

    var buttonText = 'Add';
    if (inProgress) {
      buttonText = 'Adding...';
      canAdd = false;
    }

    var value = this.state.value;
    var addButtonDisabled = (canAdd && value) ? '' : 'disabled';

    return (
      <div className="form-group">
        <label htmlFor="revset">Revset</label>
        <div className="input-group">
          <input
            ref="revset"
            placeholder="Revset"
            type="text"
            value={value}
            onKeyDown={this.handleKeyDown}
            onChange={this.handleChange}
            className="form-control" />
          <span className="input-group-btn">
            <button onClick={this.handleAdd}
              disabled={addButtonDisabled}
              type="button"
              style={{width: '100px'}}
              className="btn btn-default">{buttonText}</button>
          </span>
        </div>
      </div>
    );
  }
});

module.exports = RevsetField;
