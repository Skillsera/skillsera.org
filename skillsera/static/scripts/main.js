var redux;
$(function() {
  "use strict";

  redux = {};

  var linkifyDependencies = function(dependencies) {
    var links = [];
    for (var dependency in dependencies) {
      var d = dependencies[dependency];
      links.push('<a href="/admin?id=' + d.id + '">' + d.question + '</a>');
    }
    return links.join(', ');
  }

  //$(document).on("click", "#create_question", function() {
  //  console.log('#question').text;
  //});

  // Question.latest(function(latest) { console.log(latest); });


  var AskComponent = {
    render: function() {
      $('#app').append(
      '<div class="answerbox"></div>' +
      '<div id="ask">' +
        '<h3>Submit Question</h3>' +
        '<form method="POST" action="http://api.skillsera.org/questions" target="_blank">' +
          '<input type="text" name="question" id="question" placeholder="question"/>' +
          '<input type="text" name="topics" id="topics" placeholder="topic_1;...;topic_n"/>' +
          '<input type="text" name="dependencies" id="dependencies"' +
          'placeholder="dep_id_1;...;dep_id_n"/>' +
          '<input type="submit" id="submit_question"/>' +
        '</form>' +
      '</div>');
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

  var load = function(sid) {
    Question.get(sid, function(q) {
      $('.answerbox').empty();
      $('.answerbox').append('<h2>' + q.question +'</h2><hr/>');
      $('.answerbox').append('<iframe width="560" height="315" src="' + q.answers[0].url.replace('watch?v=', 'embed/') + '" frameborder="0" allowfullscreen></iframe>');
    });
  }

  // When user clicks li
  $(document).on("mousedown", ".awesomplete ul li", function(e) {
    var sid = $(this).attr('sid');
    console.log(sid);
    $('#searchBox').attr('sid', sid);
    load($('#searchBox').attr('sid'));
  });

  // when user types key
  $(document).on("keyup", "#searchBox", function(e) {
    // when user presses enter to select
    if (e.which === 13) {
      var sid = $('.awesomplete ul li[aria-selected="true"]').attr('sid');
      console.log(sid);
      $('#searchBox').attr('sid', sid);
      load($('#searchBox').attr('sid'));
      return;
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

  var QuestionComponent = {
    render: function(question) {
      $('.questions').empty();
      $('#app').append(
        '<div class="question">' +
          '<h3>' + question.question + '</h3>' + 
          '<hr/>' +
          '<h4>Answers</h4>' +
          question.answers + 
        '</div>');
    }
  };

  var QuestionIndexComponent = {
    render: function(questions) {
      $('#app').append(
        '<div class="questions">' +
          '<h3>Questions</h3>' +
          '<table id="questions" class="table">' +
            '<thead>' + 
              '<th>id</th>' + 
              '<th>question</th>' +
              '<th>answers</th>' +
              '<th>topics</th>' +
              '<th>depends on</th>' +
              '<th>created</th>' +
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
            '<td><a href="/admin?id=' + q.id + '">' + q.question + '</a></td>' +
            '<td>' + (JSON.stringify(q.answers) || '[]') + '</td>' +
            '<td>' + (JSON.stringify(q.topics) || '[]') + '</td>' +
            '<td>' + (linkifyDependencies(q.dependencies) || '[]') + '</td>' +
            '<td>' + q.created + '</td>' +
            '<td>' + q.dark + '</td>' +
            '<td><form method="POST" action="http://api.skillsera.org/questions/' + q.id + '?action=delete"><input type="submit" value="X">' +
            '</tr>');
      });   
    }
  }

  // init
  var options = Browser.getJsonFromUrl();
  var seedId = Browser.getUrlParameter('id');
  if (seedId) {
    try {
      Question.get(seedId, function(question) {
        QuestionComponent.render(question)
      });
    } catch(e) {
      console.log('id must be a valid integer Entity ID');
    }
  } else {
    Question.all(function(response) {
      AskComponent.render();
      var questions = response.questions;
      if (!jQuery.isEmptyObject(questions)) {
        QuestionIndexComponent.render(questions);
      }
    });

  }

});