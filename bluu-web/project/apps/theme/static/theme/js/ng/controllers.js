'use strict';

/* Controllers */
var VALID_CLASS = 'ng-valid',
    INVALID_CLASS = 'ng-invalid',
    PRISTINE_CLASS = 'ng-pristine',
    DIRTY_CLASS = 'ng-dirty';


function CompanyAccessController(CompanyAccess, $configService, $scope) {
   /*$scope.myData = [{name: "Moroni", age: 50},
                 {name: "Tiancum", age: 43},
                 {name: "Jacob", age: 27},
                 {name: "Nephi", age: 29},
                 {name: "Enos", age: 34}];
   $scope.gridOptions = { data : 'myData' };*/

    $scope.myData = [];
    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: false
    };
    $scope.pagingOptions = {
        pageSizes: [250, 500, 1000],
        pageSize: 250,
        totalServerItems: 0,
        currentPage: 1
    };	
    $scope.setPagingData = function(data, page, pageSize){	
        var pagedData = data.slice((page - 1) * pageSize, page * pageSize);
        $scope.myData = pagedData;
        $scope.pagingOptions.totalServerItems = data.length;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };
    $scope.getPagedDataAsync = function (pageSize, page, searchText) {
        setTimeout(function () {
            var data;
            if (searchText) {
                var ft = searchText.toLowerCase();
                CompanyAccess.query({'companyId': COMPANY_ID}, function(data){
                    data.filter(function(item) {
                        return JSON.stringify(item).toLowerCase().indexOf(ft) != -1;
                    });
                    $scope.setPagingData(data,page,pageSize);
                });

                /*$http.get('http://localhost:8000/api/accounts/companies/').success(function (largeLoad) {		
                    data = largeLoad.filter(function(item) {
                        return JSON.stringify(item).toLowerCase().indexOf(ft) != -1;
                    });
                    $scope.setPagingData(data,page,pageSize);
                });*/
            } else {
                CompanyAccess.query({'companyId':COMPANY_ID}, function(data){
                    $scope.setPagingData(data,page,pageSize);
                });
                
                /*$http.get('http://localhost:8000/api/accounts/companies/').success(function (largeLoad) {
                    $scope.setPagingData(largeLoad,page,pageSize);
                });*/
            }
        }, 100);
    };
	
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
	
    $scope.$watch('pagingOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);
    $scope.$watch('filterOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);   


    $scope.columnDefs = [{ field: 'user.username', displayName: 'Username'},
                  { field: 'user.first_name', displayName: 'First Name'},
                  { field: 'user.last_name', displayName: 'Last Name'},
                  { field: 'groups[0]', displayName: 'Access'},
                  { field: 'action', displayName: 'Action', cellTemplate: '<div class="ngCellText colt2"><a href="#">Delete</a></div>'}
                  ];
	
    $scope.AccessGridOptions = {
        data: 'myData',
        displaySelectionCheckbox: false,
        plugins: [new ngGridFlexibleHeightPlugin($configService.getGridHeight())],
        //enablePaging: false,
        //pagingOptions: $scope.pagingOptions,
        //filterOptions: $scope.filterOptions,
        columnDefs: 'columnDefs',
        footerVisible: false
    };
}
CompanyAccessController.$inject = ['CompanyAccess', '$configService',
                                   '$scope'];


function CompanyInvitationController(CompanyAccess, CompanyAccessGroups,
                                     $configService, $scope) {
    $scope.company_access = new CompanyAccess();
    //$scope.company_access_groups = new CompanyAccessGroups();

    //CompanyAccessGroups.query({'companyId':COMPANY_ID}, function(data){
    //    $scope.group = data;
    //});

    $scope.save = function () {
        $scope.invitationData.push({email: $scope.company_access.email, invitation: 'pending'});

        if (!$scope.$$phase) {
            $scope.$apply();
        }

        CompanyAccess.save({'companyId':COMPANY_ID}, $scope.company_access,
            function (res){
                if (res.ok === 1) { console.log('success');}
                access_datatable.fnDraw();
            }
        );
    };

    $scope.invitationColumnDefs = [{ field: 'email', displayName: 'E-mail'},
        { field: 'invitation', displayName: 'Status'},
        { field: 'action', displayName: 'Action', cellTemplate: '<div class="ngCellText colt2"><a href="#">Resend</a></div>' }];

    $scope.invitationData = [
       {email: 'ian.nowitzki@example.com', invitation: 'pending'},
       {email: 'roberto.gonzales@example.com', invitation: 'pending'}
    ];
    $scope.InvitationGridOptions = { data : 'invitationData',
       displaySelectionCheckbox: false,
       plugins: [new ngGridFlexibleHeightPlugin($configService.getGridHeight())],
       columnDefs: 'invitationColumnDefs',
       footerVisible: false
    };

}
CompanyInvitationController.$inject = ['CompanyAccess', 'CompanyAccessGroups',
                                      '$configService', '$scope'];


function CompanySitesController(Site, $configService, $scope) {
    $scope.myData = [];
    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: false
    };
    $scope.pagingOptions = {
        pageSizes: [250, 500, 1000],
        pageSize: 250,
        totalServerItems: 0,
        currentPage: 1
    };	
    $scope.setPagingData = function(data, page, pageSize){	
        var pagedData = data.slice((page - 1) * pageSize, page * pageSize);
        $scope.myData = pagedData;
        $scope.pagingOptions.totalServerItems = data.length;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };
    $scope.getPagedDataAsync = function (pageSize, page, searchText) {
        setTimeout(function () {
            var data;
            if (searchText) {
                var ft = searchText.toLowerCase();
                Site.query({'companyId': COMPANY_ID}, function(data){
                    data.filter(function(item) {
                        return JSON.stringify(item).toLowerCase().indexOf(ft) != -1;
                    });
                    $scope.setPagingData(data,page,pageSize);
                });
            } else {
                Site.query({'companyId':COMPANY_ID}, function(data){
                    $scope.setPagingData(data,page,pageSize);
                });
            }
        }, 100);
    };
	
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
	
    $scope.$watch('pagingOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);
    $scope.$watch('filterOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);   


    $scope.columnDefs = [{ field: 'first_name', displayName: 'First Name'},
                  { field: 'last_name', displayName: 'Last Name'},
                  { field: 'city', displayName: 'City'},
                  { field: 'street', displayName: 'Street'},
                  { field: 'action', displayName: 'Action', cellTemplate: '<div class="ngCellText colt2"><a href="#">Delete</a></div>'}
                  ];
	
    $scope.CompanySitesGridOptions = {
        data: 'myData',
        displaySelectionCheckbox: false,
        //plugins: [new ngGridFlexibleHeightPlugin($configService.getGridHeight())],
        enablePaging: true,
        pagingOptions: $scope.pagingOptions,
        //filterOptions: $scope.filterOptions,
        columnDefs: 'columnDefs',
        footerVisible: true,
        canSelectRows: false
    };
    $scope.site = new Site();

    $scope.save = function(){
        $scope.site.$save({'companyId':COMPANY_ID}, function(res){
            $scope.myData.push(res);
            $scope.site = new Site();
            $scope.newsite.$setPristine();
            $('#sites-tab a[href="#sites"]').tab('show');
        }, function(res){
            if (res.status === 400){
                var field;
                for(field in res.data){
                    console.log(res.data[field]);
                    $scope.newsite.$setDirty();
                    $scope.newsite[field].$setValidity(false);
                    $scope.newsite[field].$dirty = true;
                    var element_string = 'form[name="newsite"] [name="' + field + '"]';
                    var $element = angular.element(element_string);
                    $element.removeClass(PRISTINE_CLASS);
                    $element.addClass(DIRTY_CLASS);
                }
            }
        });
    };
}
CompanySitesController.$inject = ['Site', '$configService', '$scope'];

function CompanySiteCreateController(Site, $configService, $scope) {
    //$scope.site = new Site();

    //$scope.saver = function(){
    //    console.log('saving');
    //    $scope.site.$save({'companyId':COMPANY_ID}, function(res){console.log('done');});
    //};
} 
CompanySiteCreateController.$inject = ['Site', '$configService', '$scope'];


function SiteAccessController(SiteAccess, $configService, $scope) {
    $scope.myData = [];
    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: false
    };
    $scope.pagingOptions = {
        pageSizes: [250, 500, 1000],
        pageSize: 250,
        totalServerItems: 0,
        currentPage: 1
    };	
    $scope.setPagingData = function(data, page, pageSize){	
        var pagedData = data.slice((page - 1) * pageSize, page * pageSize);
        $scope.myData = pagedData;
        $scope.pagingOptions.totalServerItems = data.length;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };
    $scope.getPagedDataAsync = function (pageSize, page, searchText) {
        setTimeout(function () {
            var data;
            if (searchText) {
                var ft = searchText.toLowerCase();
                SiteAccess.query({'siteId': SITE_ID}, function(data){
                    data.filter(function(item) {
                        return JSON.stringify(item).toLowerCase().indexOf(ft) != -1;
                    });
                    $scope.setPagingData(data,page,pageSize);
                });
            } else {
                SiteAccess.query({'siteId':SITE_ID}, function(data){
                    $scope.setPagingData(data,page,pageSize);
                });
            }
        }, 100);
    };
	
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
	
    $scope.$watch('pagingOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);
    $scope.$watch('filterOptions', function () {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }, true);   


    $scope.columnDefs = [{ field: 'user.username', displayName: 'Username'},
                  { field: 'user.first_name', displayName: 'First Name'},
                  { field: 'user.last_name', displayName: 'Last Name'},
                  { field: 'groups[0]', displayName: 'Access'},
                  { field: 'action', displayName: 'Action', cellTemplate: '<div class="ngCellText colt2"><a href="#">Delete</a></div>'}
                  ];
	
    $scope.AccessGridOptions = {
        data: 'myData',
        displaySelectionCheckbox: false,
        plugins: [new ngGridFlexibleHeightPlugin($configService.getGridHeight())],
        //enablePaging: false,
        //pagingOptions: $scope.pagingOptions,
        //filterOptions: $scope.filterOptions,
        columnDefs: 'columnDefs',
        footerVisible: false
    };
}
SiteAccessController.$inject = ['SiteAccess', '$configService', '$scope'];


function SiteInvitationController(SiteAccess, SiteAccessGroups,
                                     $configService, $scope) {
    $scope.site_access = new SiteAccess();

    SiteAccessGroups.query({'siteId':SITE_ID}, function(data){
        $scope.groups = data;
    });

    $scope.save = function () {
        $scope.invitationData.push({email: $scope.site_access.email, invitation: 'pending'});

        if (!$scope.$$phase) {
            $scope.$apply();
        }

        /*SiteAccess.save({'siteId':SITE_ID}, $scope.site_access,
            function (res){
                if (res.ok === 1) { console.log('success');}}
        );*/
    };

    $scope.invitationColumnDefs = [{ field: 'email', displayName: 'E-mail'},
        { field: 'invitation', displayName: 'Status'},
        { field: 'action', displayName: 'Action', cellTemplate: '<div class="ngCellText colt2"><a href="#">Resend</a></div>' }];

    $scope.invitationData = [
       {email: 'ian.nowitzki@example.com', invitation: 'pending'},
       {email: 'roberto.gonzales@example.com', invitation: 'pending'}
    ];
    $scope.InvitationGridOptions = { data : 'invitationData',
       displaySelectionCheckbox: false,
       plugins: [new ngGridFlexibleHeightPlugin($configService.getGridHeight())],
       columnDefs: 'invitationColumnDefs',
       footerVisible: false
    };

}
SiteInvitationController.$inject = ['SiteAccess', 'SiteAccessGroups',
                                      '$configService', '$scope'];

