var Question, Browser;
(function () {
  "use strict";

  $.support.cors = true
  var apiurl = "https://api.skillsera.org";

  var requests = {
    get: function(url, callback) {
      $.get(url, function(results) {
      }).done(function(data) {
        if (callback) { callback(data); }
      });
    },

    post: function(url, data, callback) {
      $.post(url, data, function(results) {
      }).done(function(data) {
        if (callback) { callback(data); }
      });
    },

    put: function(url, data, callback) {
      $.put(url, data, function(results) {
      }).done(function(data) {
        if (callback) { callback(data); }
      });
    },
  };

  Question = {
    get: function(id, callback) {
      var url = apiurl + '/questions/' + id;
      requests.get(url, callback);
    },
    all: function(callback) {
      var url = apiurl + '/questions';
      requests.get(url, callback);
    },
    search: function(query, callback) {
      var url = apiurl + '/questions?action=search&query=' + query + '&field=question';
      requests.get(url, callback);
    }
    //addDependency
  }

  Browser = {
    getUrlParameter: function(key) {
      var query = window.location.search.substring(1);
      var params = query.split("&");
      if (key) {
        for (var i=0;i<params.length;i++) {
          var item = params[i].split("=");
          var val = item[1];
          if(item[0] == key){return(val);}
        }
        return(undefined);
      }
      return(items);
    },
    getJsonFromUrl: function () {
      var query = location.search.substr(1);
      var result = {};
      query.split("&").forEach(function(part) {
        var item = part.split("=");
        result[item[0]] = decodeURIComponent(item[1]);
      });
      return result;
    },

    change_url: function(query) {
      var getUrl = window.location;
      var baseUrl = getUrl .protocol + "//" + getUrl.host +
        "/" + getUrl.pathname.split('/')[1];
      window.history.pushState({
        "html": document.html,
        "pageTitle": document.title + " " + query,
      }, "", baseUrl + "?id=" + query);
    }
  }
}());