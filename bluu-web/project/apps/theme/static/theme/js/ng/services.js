'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('Bluu.services', ['ngResource']).
  value('version', '0.1').
  factory('Company', function($resource){
    return $resource('/api/accounts/companies/:companyId/', {companyId: '@id'});
  }).
  factory('CompanyAccess', function($resource){
    return $resource('/api/accounts/companies/:companyId/access/');
  }).
  factory('CompanyAccessGroups', function($resource){
    return $resource('/api/accounts/companies/:companyId/access/groups/');
  }).
  factory('Sites', function($resource){
    return $resource('/api/accounts/sites/:siteId', {siteId: '@id'});
  }).
  factory('SiteAccess', function($resource){
    return $resource('/api/accounts/sites/:siteId/access/');
  }).
  factory('SiteAccessGroups', function($resource){
    return $resource('/api/accounts/sites/:siteId/access/groups/',
        {}, {
        query: { method:'GET', isArray:true }
    });
  }).
  factory('$configService', function(){
      var hgtOpts = {minHeight: 120};

      return {
          getGridHeight: function(){
            return hgtOpts;
          }
      };
  });
