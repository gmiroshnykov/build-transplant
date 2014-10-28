var $ = require('jquery');

exports.lookup = function(repository, revset, callback) {
  var url = BASE_URL + 'repositories/' + repository + '/lookup';
  var data = {revset: revset};
  $.ajax(url, {
    data: data
  }).success(function(data, status, xhr) {
    return callback(null, data);
  }).fail(function(xhr, status, error) {
    var data = $.parseJSON(xhr.responseText);
    return callback(data.error);
  });
};

exports.transplant = function(source, target, items, callback) {
  var url = BASE_URL + 'transplant';
  var data = {
    src: source,
    dst: target,
    items: items
  };
  $.ajax(url, {
    method: 'POST',
    data: JSON.stringify(data),
    contentType: 'application/json'
  }).success(function(data, status, xhr) {
    return callback(null, data);
  }).fail(function(xhr, status, error) {
    var data = $.parseJSON(xhr.responseText);
    return callback({
      message: data.error,
      details: data.details
    });
  });
};
