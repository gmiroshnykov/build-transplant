/**
 * @jsx React.DOM
 */

var React = require('react'),
    _ = require('underscore');

var Api = require('../api');

var TransplantForm = require('./TransplantForm.jsx'),
    TransplantRevsets = require('./TransplantRevsets.jsx');

var TransplantApp = React.createClass({
  getInitialState() {
    return {
      sourceRepository: '',
      targetRepository: '',
      revsets: [],
      inProgressTranslant: false,
      transplantResult: null,
      transplantDone: false
    };
  },

  handleChangeSourceRepository(sourceRepository) {
    this.setState({
      sourceRepository: sourceRepository,
      revsets: []
    });
  },

  handleChangeTargetRepository(targetRepository) {
    this.setState({targetRepository: targetRepository});
  },

  handleAddRevset(revset) {
    revset.squash = false;
    revset.squashedMessage = null;

    this.state.revsets.push(revset);
    this.forceUpdate();
  },

  handleDeleteRevset(revsetId) {
    this.state.revsets = _.reject(this.state.revsets, _.matches({revset: revsetId}));
    this.forceUpdate();
  },

  handleChangeSquash(revsetId, flag) {
    var revset = _.findWhere(this.state.revsets, {revset: revsetId});
    if (!revset) {
      return;
    }

    revset.squash = flag;
    this.forceUpdate();
  },

  handleChangeSquashedMessage(revsetId, squashedMessage) {
    var revset = _.findWhere(this.state.revsets, {revset: revsetId});
    if (!revset) {
      return;
    }

    revset.squashedMessage = squashedMessage;
    this.forceUpdate();
  },

  handleChangeCommit(revsetId, commitId, newCommit) {
    var revset = _.findWhere(this.state.revsets, {revset: revsetId});
    if (!revset) {
      return;
    }

    var oldCommit = _.findWhere(revset.commits, {node: commitId});
    if (!oldCommit) {
      return;
    }

    var index = _.indexOf(revset.commits, oldCommit);
    if (index === -1) {
      return;
    }

    revset.commits[index] = newCommit;
    this.forceUpdate();
  },

  handleTransplant() {
    var source = this.state.sourceRepository;
    var target = this.state.targetRepository;
    var revsets = this.state.revsets;

    var items = [];
    revsets.forEach(revset => {
      if (revset.squash) {
        items.push({
          revset: revset.revset,
          message: revset.squashedMessage
        });
      } else {
        revset.commits.forEach(commit => {
          items.push({
            commit: commit.node,
            message: commit.message
          });
        })
      }
    });

    this.setState({
      inProgressTranslant: true,
      transplantResult: null,
      transplantDone: false
    });

    return Api.transplant(source, target, items, (err, result) => {
      this.setState({inProgressTranslant: false})

      if (err) {
        var error = {message: err.message};
        if (err.details) {
          error.details =
            "command: " + err.details.cmd.join(' ') + "\n" +
            "returncode: " + err.details.returncode + "\n" +
            "stdout: " + err.details.stdout + "\n" +
            "stderr: " + err.details.stderr + "\n";
        }

        return this.setState({
          transplantDone: false,
          transplantResult: {
            error: error
          }
        });
      }

      return this.setState({
        transplantDone: true,
        transplantResult: {
          success: true,
          message: 'Tip: ' + result.tip
        }
      });
    });



    return;

    this.setState({
      inProgressTranslant: true,
      transplantResult: null,
      transplantDone: false
    });

    setTimeout(() => {
      this.setState({
        inProgressTranslant: false,
        transplantResult: {
          alert: 'success',
          message: 'Done'
        },
        transplantDone: true
      });
    }, 3000);
  },

  handleReset() {
    this.setState({
      revsets: [],
      inProgressTranslant: false,
      transplantResult: null,
      transplantDone: false
    });
  },

  renderButton() {
    return !this.state.transplantDone
      ? this.renderTransplantButton()
      : this.renderResetButton()
  },

  renderTransplantButton() {
    if (this.state.revsets.length < 1) {
      return;
    }

    var inPogress = this.state.inProgressTranslant;
    var disabled = inPogress;
    if (!this.state.sourceRepository || !this.state.targetRepository) {
      disabled = true;
    }

    var text = 'Transplant';
    if (inPogress) {
      text = 'Transplanting...';
    }

    return (
      <button type="button"
        disabled={disabled}
        onClick={this.handleTransplant}
        className="btn btn-primary btn-lg col-md-2 pull-right">{text}</button>
    );
  },

  renderResetButton() {
    if (this.state.revsets.length < 1) {
      return;
    }

    return (
      <button type="button"
        onClick={this.handleReset}
        className="btn btn-warning btn-lg col-md-2 pull-right">Reset form</button>
    )
  },

  renderResult() {
    var result = this.state.transplantResult;
    if (!result || !result.success) {
      return;
    }

    return (
      <div className="alert alert-success pull-left" role="alert">{result.message}</div>
    );
  },

  renderError() {
    var result = this.state.transplantResult;
    if (!result || !result.error) {
      return;
    }

    var details = result.error.details
      ? <div className="panel-body"><pre>{result.error.details}</pre></div>
      : null;

    return (
      <div className="panel panel-danger">
        <div className="panel-heading">{result.error.message}</div>
        {details}
      </div>
    );
  },

  render() {
    var result = this.renderResult();
    var button = this.renderButton();
    var error = this.renderError();

    var resultRow = null;
    if (result || button) {
      resultRow = <div className="row">
          <div className="form-group clearfix">
            {result}
            {button}
          </div>
        </div>;
    }

    var errroRow = null;
    if (error) {
      errroRow = <div className="row">{error}</div>;
    }

    return (
      <div>
        <div className="row">
          <h1>Transplant</h1>
        </div>
        <div className="row">
          <TransplantForm
            repositories={this.props.repositories}
            sourceRepository={this.state.sourceRepository}
            targetRepository={this.state.targetRepository}
            onChangeSourceRepository={this.handleChangeSourceRepository}
            onChangeTargetRepository={this.handleChangeTargetRepository}
            revsets={this.state.revsets}
            onAddRevset={this.handleAddRevset} />
        </div>
        <div className="row">
          <TransplantRevsets
            revsets={this.state.revsets}
            onChangeSquash={this.handleChangeSquash}
            onChangeCommit={this.handleChangeCommit}
            onChangeSquashedMessage={this.handleChangeSquashedMessage}
            onDelete={this.handleDeleteRevset} />
        </div>
        {resultRow}
        {errroRow}
      </div>
    );
  }
});

module.exports = TransplantApp;
