'use strict';

/* Services */
angular.module('Bluu.services', ['ngResource']).
    value('version', '0.1').
    factory('Company', function ($resource) {
        return $resource('/api/companies/:companyId/', {companyId: '@id'});
    }).
    factory('CompanyAccess', function ($resource) {
        return $resource('/api/companies/:companyId/access/:id/',
            {
                id: '@id'
            },
            {
                set_access: {method: 'PUT'}
            }
            );
    }).
    factory('Site', function ($resource) {
        return $resource('/api/companies/:companyId/sites/:siteId/', {siteId: '@id'});
    }).
    factory('SiteAccess', function ($resource) {
        return $resource('/api/sites/:siteId/access/:id/',
            {
                id: '@id'
            },
            {
                set_access: {method: 'PUT'}
            }
            );
    }).
    factory('$configService', function () {
        var hgtOpts = {minHeight: 120};

        return {
            getGridHeight: function () {
                return hgtOpts;
            }
        };
    }).
    run(function ($rootScope) {

        $rootScope.is = function(type, value) {
          return angular['is'+type](value);
        };
        /**
         * Wrapper for $.isEmptyObject()
         *
         * @param value	{mixed} Value to be tested
         * @return boolean
         */
        $rootScope.empty = function(value) {
          return $.isEmptyObject(value);
        };
        /**
         * Debugging Tools
         *
         * Allows you to execute debug functions from the view
         */
        $rootScope.log = function(variable) {
          console.log(variable);
        };
        $rootScope.alert = function(text) {
          alert(text);
        };
    });
