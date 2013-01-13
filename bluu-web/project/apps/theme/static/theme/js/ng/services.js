'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('Bluu.services', ['ngResource']).
  value('version', '0.1').
  factory('Company', function($resource){
    return $resource('/api/accounts/companies/:companyId/',
        { companyId: '@id' }, {
        query: { method:'GET', isArray:true }
    });
  }).
  factory('CompanyAccess', function($resource){
    return $resource('/api/accounts/companies/:companyId/access/',
        {}, {
        query: { method:'GET', isArray:true }
    });
  });
