'use strict';

/* Controllers */
/*var VALID_CLASS = 'ng-valid',
    INVALID_CLASS = 'ng-invalid',
    PRISTINE_CLASS = 'ng-pristine',
    DIRTY_CLASS = 'ng-dirty';

function CompanyInvitationController(CompanyAccess, CompanyAccessGroups,
                                     $configService, $scope) {
    $scope.company_access = new CompanyAccess();
    //$scope.invitationData = [];

    $scope.save = function () {
        //$scope.invitationData.push({email: $scope.company_access.email, invitation: 'pending'});

        //if (!$scope.$$phase) {
        //    $scope.$apply();
        //}

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
    $scope.save = function () {
        $scope.site_access.$save({'companyId': COMPANY_ID},
            function (res) {
                $scope.access_datatable.fnDraw();
            }
        );
    };
};
SiteInvitationController.$inject = ['SiteAccess', 'SiteAccessGroups',
                                      '$configService', '$scope'];

*/

function CompanyAccessController(CompanyAccess, $dialog, $compile, $configService, $scope) {

      $scope.company_access = new CompanyAccess();
      //$scope.invitationData = [];

      $scope.save = function () {
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
        var msgbox = $dialog.messageBox('Delete Item', 'Are you sure?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        msgbox.open().then(function(result){
            if(result === 'yes') {
                CompanyAccess.delete({'companyId':COMPANY_ID, 'id': id}, {},
                                function(data){
                                    console.log(data);
                                    $scope.access_datatable.fnDraw();
                                }); 
            }
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
                  {
                      "mData": 'access',
                      "mRender": function( data, type, full) {
                          var ret = data.email;
                          if (data.invitation == true){
                            ret += ' (pending)';
                          }
                          return ret;
                      },
                  },
                  {
                     "mData": 'access.groups',
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
                      "mData": 'access.id',
                      "mRender": function( data, type, full) {
                          return '<a ng-click="remove(' + data + ')" href="#"><i class="icon-remove"></i></a>';
                      },
                      "sWidth": "100px",
                      "bSearchable": false, 
                      "bSortable": false
                  }
              ]
      });

      $.extend( $.fn.dataTableExt.oStdClasses, {
          "sWrapper": "dataTables_wrapper form-inline"
      } );

  };
 CompanyAccessController.$inject = ['CompanyAccess', '$dialog', '$compile', '$configService', '$scope'];


function SiteAccessController(SiteAccess, $dialog, $compile, $configService, $scope) {

      $scope.site_access = new SiteAccess();
      //$scope.invitationData = [];

      $scope.save = function () {
          $scope.site_access.$save({'siteId': SITE_ID},
              function (res) {
                  $scope.site_access = new SiteAccess();
                  $scope.addForm.$setPristine();
                  $scope.access_datatable.fnDraw();
              }
              );
      };


      $scope.set = function (id, group) {
          var access = new SiteAccess({'id': id,
                                          'group': group});
          access.$set_access({'siteId':SITE_ID}, function(data){
              console.log(data);
              $scope.access_datatable.fnDraw();
          });
      };

      $scope.remove = function (id){
        var msgbox = $dialog.messageBox('Delete Item', 'Are you sure?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        msgbox.open().then(function(result){
            if(result === 'yes') {
                SiteAccess.delete({'siteId': SITE_ID, 'id': id}, {},
                                function(data){
                                    console.log(data);
                                    $scope.access_datatable.fnDraw();
                                }); 
            }
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
                  {
                      "mData": 'access',
                      "mRender": function( data, type, full) {
                          var ret = data.email;
                          if (data.invitation == true){
                            ret += ' (pending)';
                          }
                          return ret;
                      },
                  },
                  {
                     "mData": 'access.groups',
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
                      "mData": 'access.id',
                      "mRender": function( data, type, full) {
                          return '<a ng-click="remove(' + data + ')" href="#"><i class="icon-remove"></i></a>';
                      },
                      "sWidth": "100px",
                      "bSearchable": false, 
                      "bSortable": false
                  }
              ]
      });

      $.extend( $.fn.dataTableExt.oStdClasses, {
          "sWrapper": "dataTables_wrapper form-inline"
      } );

  };
 SiteAccessController.$inject = ['SiteAccess', '$dialog', '$compile', '$configService', '$scope'];

