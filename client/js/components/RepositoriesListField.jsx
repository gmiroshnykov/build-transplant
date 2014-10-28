/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');

var RepositoriesListField = React.createClass({
  propTypes: {
    title: React.PropTypes.string.isRequired,
    repositories: React.PropTypes.arrayOf(
      React.PropTypes.shape({
        name: React.PropTypes.string.isRequired,
        path: React.PropTypes.string.isRequired
      })
    )
  },

  handleChange(e) {
    e.preventDefault();

    var repository = e.target.value;
    this.props.onChange(repository);
  },

  render() {
    var repositories = [<option key="" value=""></option>];
    _.each(this.props.repositories, function(repository) {
      repositories.push(<option key={repository.name}
        value={repository.name}>{repository.name} ({repository.path})</option>)
    });

    return (
      <div className="form-group">
        <label htmlFor={this.props.name}
          className="control-label">{this.props.title}</label>
        <select name={this.props.name} value={this.props.value}
          onChange={this.handleChange} className="form-control">
          {repositories}
        </select>
      </div>
    );
  }
});

module.exports = RepositoriesListField;
