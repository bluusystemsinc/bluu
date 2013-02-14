'use strict';

/* Directives */

angular.module('Bluu.directives', []).
      directive('appVersion', ['version', function (version) {
        return function (scope, elm, attrs) {
            elm.text(version);
        };
    }]).
    directive('CompanyAccessDatatable', function () {
      
    });
