'use strict';

/* Controllers */
var VALID_CLASS = 'ng-valid',
    INVALID_CLASS = 'ng-invalid',
    PRISTINE_CLASS = 'ng-pristine',
    DIRTY_CLASS = 'ng-dirty';


function CompanyAccessListController(CompanyAccess, $configService, $scope) {
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
CompanyAccessListController.$inject = ['CompanyAccess', '$configService',
                                   '$scope'];


function CompanyInvitationController(CompanyAccess, CompanyAccessGroups,
                                     $configService, $scope) {
    $scope.company_access = new CompanyAccess();
    $scope.invitationData = [];

    $scope.save = function () {
        $scope.invitationData.push({email: $scope.company_access.email, invitation: 'pending'});

        if (!$scope.$$phase) {
            $scope.$apply();
        }

        $scope.company_access.$save({'companyId': COMPANY_ID},
            function (res) {
                $scope.access_datatable.fnDraw();
            }
            );
    };

}
CompanyInvitationController.$inject = ['CompanyAccess', 'CompanyAccessGroups',
                                      '$configService', '$scope'];


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
};
SiteInvitationController.$inject = ['SiteAccess', 'SiteAccessGroups',
                                      '$configService', '$scope'];


function CompanyAccessController(CompanyAccess, $compile, $configService, $scope) {

      $scope.company_access = new CompanyAccess();
      //$scope.invitationData = [];

      $scope.save = function () {
          //$scope.invitationData.push({email: $scope.company_access.email, invitation: 'pending'});

          /*if (!$scope.$$phase) {
              $scope.$apply();
          }*/

          $scope.company_access.$save({'companyId': COMPANY_ID},
              function (res) {
                  $scope.company_access = new CompanyAccess();
                  $scope.addForm.$setPristine();
                  $scope.access_datatable.fnDraw();
              }
              );
      };


      $scope.set = function (id, group) {
          var access = new CompanyAccess({'id': id,
                                          'group': group});
          access.$set_access({'companyId':COMPANY_ID}, function(data){
              console.log(data);
              $scope.access_datatable.fnDraw();
          });
      };

      $scope.remove = function (id){
         CompanyAccess.delete({'companyId':COMPANY_ID, 'id': id}, {},
                                function(data){
                                    console.log(data);
                                    $scope.access_datatable.fnDraw();
                                }); 
      }
      
      var rowCompiler = function (nRow, aData, iDataIndex){
          var linker = $compile(nRow);
          nRow = linker($scope);
      };

      $scope.access_datatable = $('#access_list_table').dataTable( {
           "oLanguage": DATATABLE_TRANS,
          "sDom": "<'row-fluid'r>t<'row-fluid'<'span6'i><'span6'p>>",
           "bServerSide": true,
           //"bProcessing": true,
           "bPaginate": false,
           "bFilter": false,
           "sAjaxSource": DATATABLE_URL,
           "aaSorting": [[0, 'asc']],
           "fnCreatedRow": rowCompiler,
           "aoColumns": [
                  { "mData": 'access.email'},
                  {
                     "mData": 'groups',
                      "fnCreatedCell": function(nTd, sData, oData, iRow, iCol)
                      {
                          $(nTd).css('text-align', 'center');
                      },
                    "sWidth": "145px",
                    "bSearchable": false, 
                    "bSortable": false
                  },
                  {
                      "fnCreatedCell": function(nTd, sData, oData, iRow, iCol)
                      {
                          $(nTd).css('text-align', 'center');
                      },
                      "mData": 'access',
                      "mRender": function( data, type, full) {
                          return '<a ng-click="remove(' + data.id + ')" href="#"><i class="icon-remove"></i></a>';
                      },
                      "sWidth": "10%",
                      "bSearchable": false, 
                      "bSortable": false
                  }
              ]
      });

      $.extend( $.fn.dataTableExt.oStdClasses, {
          "sWrapper": "dataTables_wrapper form-inline"
      } );

  };
 CompanyAccessController.$inject = ['CompanyAccess', '$compile', '$configService', '$scope'];

