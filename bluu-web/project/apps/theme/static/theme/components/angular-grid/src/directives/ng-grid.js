﻿ngGridDirectives.directive('ngGrid', ['$compile', '$filter', 'SortService', 'DomUtilityService', function($compile, $filter, sortService, domUtilityService) {
    var ngGrid = {
        scope: true,
        compile: function() {
            return {
                pre: function($scope, iElement, iAttrs) {
                    var $element = $(iElement);
                    var options = $scope.$eval(iAttrs.ngGrid);
                    options.gridDim = new ng.Dimension({ outerHeight: $($element).height(), outerWidth: $($element).width() });
                    var grid = new ng.Grid($scope, options, sortService, domUtilityService, $filter);

                    // if columndefs are a string of a property ont he scope watch for changes and rebuild columns.
                    if (typeof options.columnDefs == "string") {
                        $scope.$parent.$watch(options.columnDefs, function(a) {
                            $scope.columns = [];
                            grid.config.columnDefs = a;
                            grid.buildColumns();
                            grid.eventProvider.assignEvents();
							domUtilityService.RebuildGrid($scope,grid);
                        });
                    } else {
						grid.buildColumns();
					}
					
                    // if it is a string we can watch for data changes. otherwise you won't be able to update the grid data
                    if (typeof options.data == "string") {
                        $scope.$parent.$watch(options.data, function (a) {
                            // make a temporary copy of the data
                            grid.data = $.extend(true, [], a);
                            var diff = grid.data.length - grid.rowCache.length;
                            if (diff < 0) {
                                grid.rowCache.length = grid.rowMap.length = grid.data.length;
                            } else {
                                for (var i = grid.rowCache.length; i < grid.data.length; i++) {
                                    grid.rowCache[i] = grid.rowFactory.buildEntityRow(grid.data[i], i);
                                }
                            }
                            angular.forEach(grid.data, function (item, j) {
                                if (grid.rowCache[j]) {
                                    if (!angular.equals(grid.rowCache[j].entity, item)) {
                                        grid.rowCache[j].entity = item;
                                        grid.rowCache[j].modelIndex = j;
                                        grid.rowCache[j].setSelection(false);
                                    }
                                    grid.rowMap[j] = j;
                                }
                            });
                            grid.searchProvider.evalFilter();
                            grid.configureColumnWidths();
                            grid.refreshDomSizes();
                            if (grid.config.sortInfo) {
                                if (!grid.config.sortInfo.column) {
                                    grid.config.sortInfo.column = $scope.columns.filter(function(c) {
                                        return c.field == grid.config.sortInfo.field;
                                    })[0];
                                    if (!grid.config.sortInfo.column) {
                                        return;
                                    }
                                }
                                grid.config.sortInfo.column.sortDirection = grid.config.sortInfo.direction.toLowerCase();
                                grid.sortData(grid.config.sortInfo.column);
                            }
                            $scope.$emit("ngGridEventData");
                        }, true);
                    }
					
                    grid.footerController = new ng.Footer($scope, grid);
                    //set the right styling on the container
                    iElement.addClass("ngGrid").addClass(grid.gridId.toString());
                    if (options.jqueryUITheme) {
                        iElement.addClass('ui-widget');
                    }
                    iElement.append($compile(ng.gridTemplate())($scope)); // make sure that if any of these change, we re-fire the calc logic
                    //walk the element's graph and the correct properties on the grid
                    domUtilityService.AssignGridContainers($scope, iElement, grid);
                    //now use the manager to assign the event handlers
                    grid.eventProvider = new ng.EventProvider(grid, $scope, domUtilityService);
                    //initialize plugins.
                    angular.forEach(options.plugins, function (p) {
                        if (typeof p === 'function') {
                            p.call(this, []).init($scope.$new(), grid, { SortService: sortService, DomUtilityService: domUtilityService });
                        } else {
                            p.init($scope.$new(), grid, { SortService: sortService, DomUtilityService: domUtilityService });
                        }
                    });
                    // method for user to select a specific row programatically
                    options.selectRow = function (rowIndex, state) {
                        if (grid.rowCache[rowIndex]) {
                            grid.rowCache[rowIndex].setSelection(state ? true : false);
                        }
                    };
                    // method for user to select the row by data item programatically
                    options.selectItem = function (itemIndex, state) {
                        options.selectRow(grid.rowMap[itemIndex], state);
                    };					
					
					$scope.$on('ngGridEventDigestGrid', function(){
						domUtilityService.digest($scope.$parent);
					});			
					
					$scope.$on('ngGridEventDigestGridParent', function(){
						domUtilityService.digest($scope.$parent);
					});

                    return null;
                }
            };
        }
    };
    return ngGrid;
}]);