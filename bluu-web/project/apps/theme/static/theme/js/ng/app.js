'use strict';


// Declare app level module which depends on filters, and services
var app = angular.module('Bluu', ['ui', 'ui.bootstrap.dialog', 'Bluu.filters', 'Bluu.services', 'Bluu.directives']).
  config(['$httpProvider', function($httpProvider) {
      var authToken;
      authToken = $('meta[name="csrf-token"]').attr('content');
      $httpProvider.defaults.headers.common['X-CSRFTOKEN'] = authToken;
  }]).
  config(['$dialogProvider', function($dialogProvider){
            var t = '<div class="modal-header">' +
                    '<h1>{{ title }}</h1>' +
                    '</div>' +
                    '<div class="modal-body">' +
                    '<p>{{ message }}</p>' +
                    '</div>' +
                    '<div class="modal-footer">' +
                    '<button ng-repeat="btn in buttons" ng-click="close(btn.result)" class=btn ng-class="btn.cssClass">{{ btn.label }}</button>' +
                    '</div>';
                 
    $dialogProvider.options({template: t, backdropClick: false, modalFade: true});  
  }]);

  //config(['$routeProvider', function($routeProvider) {
  //  $routeProvider.when('/view1', {templateUrl: 'partials/partial1.html', controller: MyCtrl1});
  //  $routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: MyCtrl2});
  //  $routeProvider.otherwise({redirectTo: '/view1'});
  //}]);
  //
  //

