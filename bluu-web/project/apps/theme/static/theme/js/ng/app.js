'use strict';


// Declare app level module which depends on filters, and services
angular.module('Bluu', ['ui', 'ngGrid', 'Bluu.filters', 'Bluu.services', 'Bluu.directives']).
config(['$httpProvider', function($httpProvider) {
    var authToken;
    authToken = $('meta[name="csrf-token"]').attr('content');
    $httpProvider.defaults.headers.common['X-CSRFTOKEN'] = authToken;
}]);

  //config(['$routeProvider', function($routeProvider) {
  //  $routeProvider.when('/view1', {templateUrl: 'partials/partial1.html', controller: MyCtrl1});
  //  $routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: MyCtrl2});
  //  $routeProvider.otherwise({redirectTo: '/view1'});
  //}]);
  //
  //

