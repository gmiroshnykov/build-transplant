/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');

var Api = require('../api');

var RepositoriesListField = require('./RepositoriesListField.jsx'),
    RevsetField = require('./RevsetField.jsx'),
    Alerts = require('./Alerts.jsx');

var TransplantForm = React.createClass({
  propTypes: {
    repositories: React.PropTypes.arrayOf(
      React.PropTypes.shape({
        name: React.PropTypes.string.isRequired
      })
    ),
    sourceRepository: React.PropTypes.string.isRequired,
    targetRepository: React.PropTypes.string.isRequired,
    revsets: React.PropTypes.arrayOf(
      React.PropTypes.shape({
        revset: React.PropTypes.string.isRequired
      })
    ),
    onChangeSourceRepository: React.PropTypes.func.isRequired,
    onChangeTargetRepository: React.PropTypes.func.isRequired
  },

  getInitialState() {
    return {
      inProgress: false,
      alerts: []
    };
  },

  handleAddRevset(revset) {
    var sourceRepository = this.props.sourceRepository;
    if (!sourceRepository || !revset) {
      return;
    }

    var existingRevset = _.findWhere(this.props.revsets, {revset: revset});
    if (existingRevset) {
      this.alertAdd('danger', "Revset '" + revset + "' already added", 'error_already_added');
      return;
    }

    this.setState({inProgress: true});

    return Api.lookup(sourceRepository, revset, (err, result) => {
      this.setState({inProgress: false});

      if (err) {
        this.alertAdd('danger', err, 'error');
        return;
      }

      this.refs.revsetField.reset();

      result.revset.revset = revset;
      this.props.onAddRevset(result.revset);
    });
  },

  lastAlertId: 0,

  alertAdd(type, message, id) {
    id = id || this.lastAlertId++;

    this.state.alerts.push({
      id: id,
      type: type,
      message: message
    });
    this.forceUpdate();
  },

  alertRemove(id) {
    this.state.alerts = _.reject(this.state.alerts, _.matches({id: id}));
    this.forceUpdate();
  },

  render() {
    var sourceRepository = this.props.sourceRepository;
    var targetRepository = this.props.targetRepository;

    var sourceRepositories = targetRepository == ''
      ? this.props.repositories
      : _.reject(this.props.repositories, _.matches({name: targetRepository}));

    var targetRepositories = sourceRepository == ''
      ? this.props.repositories
      : _.reject(this.props.repositories, _.matches({name: sourceRepository}));

    var canAdd = !!sourceRepository;

    return (
      <form className="transplantForm" role="form">
        <RepositoriesListField
          name="source"
          title="Source"
          value={sourceRepository}
          repositories={sourceRepositories}
          onChange={this.props.onChangeSourceRepository} />
        <RepositoriesListField
          name="target"
          title="Target"
          value={targetRepository}
          repositories={targetRepositories}
          onChange={this.props.onChangeTargetRepository} />
        <RevsetField
          ref="revsetField"
          canAdd={canAdd}
          inProgress={this.state.inProgress}
          onAdd={this.handleAddRevset} />
        <Alerts items={this.state.alerts}
          onDismiss={this.alertRemove} />
      </form>
    );
  }
});

module.exports = TransplantForm;
