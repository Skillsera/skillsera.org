var redux;
$(function() {
  "use strict";

  redux = {};

  var linkifyDependencies = function(dependencies) {
    var links = [];
    for (var dependency in dependencies) {
      var d = dependencies[dependency];
      links.push('<a href="/learn?id=' + d.id + '">' + d.question + '</a>');
    }
    return links.join(', ');
  }

  var normalizeQuestion = function(q) {
    return unescape(q.replace(/\+/g,' '));
  }

  var SubmitAnswerComponent = {
    render: function(id) {
      $('#app').append(
          '<div id="answer">' + 
            '<p>Can you contribute a video which answers this question?</p>' +
            '<form method="POST" action="https://api.skillsera.org/answers" target="_blank">' +
              '<input placeholder="youtube url" name="url"/>' +
              '<input type="number" placeholder="start time" name="start"/>' +
              '<input type="number" placeholder="stop time" name="stop"/>' +
              '<input type="hidden" value="' + id + '"/>' +
              '<input type="submit"/>' + 
            '</form>' +
          '</div>'
      );
    }
  }


  var AskQuestionComponent = {
    render: function(question, editable, parent) {
      var e = parent || '#app';
      var editable = editable || true;
      var q = question || '';
      $(e).append(
      '<div id="ask">' +
        '<form method="POST" action="https://api.skillsera.org/questions" target="_blank">' +
          '<input type="text" name="question" id="question" value="' + q + '" placeholder="question"/>' +
          '<input type="text" name="topics" id="topics" placeholder="topic_1;...;topic_n"/>' +
          '<input type="text" name="dependencies" id="dependencies"' +
          'placeholder="dep_id_1;...;dep_id_n"/>' +
          '<input type="submit" id="submit_question"/>' +
        '</form>' +
      '</div>');
    }
  }

  var SubmitQuestionComponent = function(q) {
    $('#app').append(
      "<h3>Wow! You're the first to ask: " + q + '</h3>' +
        "<p>Submit your question to the Skillsera community and we'll see if anyone knows a good video which explains the answer!</p>");
    AskQuestionComponent.render(q, false);
  }

  var QuestionListComponent = {
    render: function(questions) {
      $('#app').append(
        '<div class="questions">' +
          '<table id="questions" class="table">' +
            '<thead>' + 
              '<th>id</th>' + 
              '<th>question</th>' +
              '<th>answers</th>' +
              '<th>topics</th>' +
              '<th>requires</th>' +
              '<th>asked</th>' +
              '<th>darked?</th>' +
              '<th></th>' +
            '</thead>' +
            '<tbody id="questions">' +
            '</tbody>' + 
          '</table>' +
        '</div>');
      $(questions).each(function(index, q) {
        $('#questions').append(
          '<tr>' +
            '<td>' + q.id + '</td>' +
            '<td><a href="/learn?id=' + q.id + '">' + q.question + '</a></td>' +
            '<td>' + (JSON.stringify(q.answers) || '[]') + '</td>' +
            '<td>' + (JSON.stringify(q.topics) || '[]') + '</td>' +
            '<td>' + (linkifyDependencies(q.dependencies) || '[]') + '</td>' +
            '<td>' + q.created + '</td>' +
            '<td>' + q.dark + '</td>' +
            '<td><form method="POST" action="https://api.skillsera.org/questions/' + q.id + '?action=delete"><input type="submit" value="X">' +
            '</tr>');
      });   
    }
  }

  var serp = new Awesomplete(document.getElementById("searchBox"), {
    list: [{label: '', data: ''}],
    item: function(text, input) {
      var li = document.createElement('li');
      li.setAttribute('aria-selected', false);
      li.setAttribute('sid', text.value);
      li.textContent = text.label;
      return li;
    },
    replace: function(text) {
      this.input.value = text;
    }
  });

  var VideoAnswerComponent = {
    render: function(url, start, stop) {
      url = url.replace('watch?v=', 'embed/');
      start = start || "";
      stop = stop || "";
      return '<iframe width="560" height="315" src="' + url + '?enablejsapi=1&controls=1&start=' + start + '&end=' + stop + '&cc_load_policy=1" frameborder="0" allowfullscreen></iframe>';
    }
  }

  var loadSkillPage = {
    clear: function() {
      $('#app').remove('.answerbox');
      $('#app').append('<div class="answerbox"></div>');
    },
    render: function(sid, callback) {
      this.clear();
      Question.get(sid, function(q) {
        $('.answerbox').append('<h2>' + q.question +'</h2><hr/>');

        var answer = q.answers[0];
        if (answer) {
          $('.answerbox').append(VideoAnswerComponent.render(answer.url, answer.start, answer.stop));
          SubmitAnswerComponent.render(seedId);
        }

        if (callback) {
          callback(answer);
        }
      });
    }
  }

  var searchSubmit = function(sid) {
    var url = (window.location.pathname != "/learn") ? window.location.host + '/learn' : null;
    insertParam('id', sid, url);
    $('#searchBox').attr('sid', sid);
    loadSkillPage.render(sid);
  }


  // When user clicks li
  $(document).on("mousedown", ".awesomplete ul li", function(e) {
    var sid = $(this).attr('sid');
    searchSubmit(sid);
  });

  var getBestMatch = function(s, callback) {
    Question.search(s, function(matches) {
      if (callback) {
        callback(matches.questions[0]);
      }
    });
  }

  // when user types key
  $(document).on("keyup", "#searchBox", function(e) {
    // when user presses enter to select
    var sid = $('.awesomplete ul li[aria-selected="true"]').attr('sid');
    if (e.which === 13) {
      alert('?');
      if (sid) {
        console.log(sid);
        return searchSubmit(sid);
      } else {
        getBestMatch($('#searchBox').val(), function(match) {
          console.log($('#searchBox').val());
          console.log(match.id);
          searchSubmit(match.id);
        });
      }
    }

    if (e.keyCode === 38 || e.keyCode === 40 || e.keyCode ===27 || e.keyCode === 37 || e.keyCode === 39 || e.keyCode === 17 || e.which === 17) {
      return;
    }
    if (e.keyCode === 220) {
      return;
    }

    Question.search($('#searchBox').val(), function(matches) {
      var questions = matches.questions;
      
      if (questions) {        
        questions = questions.concat({question: "Don't see your question listed? Ask: " + $('#searchBox').val(), id: null});
        serp.list = questions.map(function(q){ return {label: q.question, value: q.id};});
      }
    });
  });





  var seedOnLoad = function(seedId) {
    try {
      Question.get(seedId, function(question) {
        loadSkillPage.render(seedId, function(answer) {
          if (!answer) {
            $('.answerbox').append(
              "<h3>No answers yet which teach this skill</h3>"
            );
            SubmitAnswerComponent.render(seedId);
          }
        });
      });
    } catch(e) {
      console.log('id must be a valid integer Entity ID');
    }
  }

  // init
  var options = Browser.getJsonFromUrl();
  var q = Browser.getUrlParameter('q');
  var seedId = Browser.getUrlParameter('id');
  if (q) {
    getBestMatch(q, function(match) {
      if (match) {
        seedOnLoad(match.id);        
      } else {
        SubmitQuestionComponent(normalizeQuestion(q));
      }
    });
  } else if (seedId) {
    seedOnLoad(seedId);
  } else {
    Question.all(function(response) {
      var questions = response.questions;
      if (!jQuery.isEmptyObject(questions)) {
        $('#app').append('<h3>Recent Question</h3><hr>');
        QuestionListComponent.render(questions);
      }
    });

  }

  function insertParam(key, value, url)
  {
    key = encodeURI(key); value = encodeURI(value);

    var kvp = document.location.search? document.location.search.substr(1).split('&') : [];
    
    var i=kvp.length; var x; while(i--) 
    {
      x = kvp[i].split('=');

      if (x[0]==key)
      {
        x[1] = value;
        kvp[i] = x.join('=');
        break;
      }
    }

    if(i<0) {kvp[kvp.length] = [key,value].join('=');}

    if (url) {
      window.location.replace(
        window.location.protocol + '//' + window.location.host + '/learn?' + kvp.join('&'));
    } else {
      document.location.search = kvp.join('&');
    }
  }

});