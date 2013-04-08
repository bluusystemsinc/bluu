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
              },
              function (res) {
                for (var key in res.data['errors']) {
                  if (res.data['errors'].hasOwnProperty(key)) {
                    $('.invite-message-placeholder').html('<div class="alert alert-error content-wrapper">'+
                        '<button class="close" data-dismiss="alert">×</button>' +
                        res.data['errors'][key] + '</div>');
                  }
                }

              }
              );
      };


      $scope.set = function (id, group, current_user_access_id) {

          var set_access = function(id, group){  
              var access = new CompanyAccess({'id': id,
                                              'group': group});
              access.$set_access({'companyId':COMPANY_ID}, function(data){
                  if (id == current_user_access_id){
                    window.location = '/';  //window.location;
                  }else{
                     $scope.access_datatable.fnDraw();
                  }
              });
          }

          if (id === current_user_access_id){
              var msgbox = $dialog.messageBox('Change own access', 'Are you sure you want to change your own access level?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);

              msgbox.open().then(function(result){
                if(result === 'yes') {
                    set_access(id, group);  
                }
              });
          }else{
            set_access(id, group);  
          }
      };

      $scope.remove = function (id, current_user_access_id){
        if (id === current_user_access_id){
            var msgbox = $dialog.messageBox('Remove own access', 'Are you sure you want to remove your own access?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        }else{
            var msgbox = $dialog.messageBox('Remove access', 'Are you sure?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        }
        msgbox.open().then(function(result){
            if(result === 'yes') {
                CompanyAccess.delete({'companyId':COMPANY_ID, 'id': id}, {},
                                function(data){
                                    if (id == current_user_access_id){
                                        window.location = '/';
                                    }else{
                                        $scope.access_datatable.fnDraw();
                                    }
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
                    "sWidth": "160px",
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
                          return '<a ng-click="remove(' + data.id + ', ' + data.current_user_access_id + ')" href="#"><i class="icon-remove"></i></a>';
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
              },
              function (res) {
                    for (var key in res.data['errors']) {
                      if (res.data['errors'].hasOwnProperty(key)) {
                        $('.invite-message-placeholder').html('<div class="alert alert-error content-wrapper">'+
                            '<button class="close" data-dismiss="alert">×</button>' +
                            res.data['errors'][key] + '</div>');
                      }
                    }
              }
          );
      };


      $scope.set = function (id, group, current_user_access_id) {

          var set_access = function(id, group){  
              var access = new SiteAccess({'id': id,
                                           'group': group});
              access.$set_access({'siteId':SITE_ID}, function(data){
                  if (id == current_user_access_id){
                    window.location = '/'; //window.location;
                  }else{
                     $scope.access_datatable.fnDraw();
                  }
              });
          }

          if (id === current_user_access_id){
              var msgbox = $dialog.messageBox('Change own access', 'Are you sure you want to change your own access level?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);

              msgbox.open().then(function(result){
                if(result === 'yes') {
                    set_access(id, group);  
                }
              });
          }else{
            set_access(id, group);  
          }
      };

      $scope.remove = function (id, current_user_access_id){
        if (id === current_user_access_id){
            var msgbox = $dialog.messageBox('Remove own access', 'Are you sure you want to remove your own access?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        }else{
            var msgbox = $dialog.messageBox('Remove access', 'Are you sure?', [{label:'Yes, I\'m sure', result: 'yes'},{label:'Nope', result: 'no'}]);
        }
        msgbox.open().then(function(result){
            if(result === 'yes') {
                SiteAccess.delete({'siteId': SITE_ID, 'id': id}, {},
                                function(data){
                                    if (id == current_user_access_id){
                                        window.location = '/'; //window.location;
                                    }else{
                                        $scope.access_datatable.fnDraw();
                                    }
                                }                                
                                ); 
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
                    "sWidth": "160px",
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
                          return '<a ng-click="remove(' + data.id +', ' + data.current_user_access_id + ')" href="#"><i class="icon-remove"></i></a>';
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


function AlertConfController(AlertConf, $compile, $configService, $scope) {
      $scope.set_alert = function (device_id, alert_id, time, unit, text, email, user) {
            var user_alert_conf = new AlertConf({'device_id': device_id,
                                                 'alert_id': alert_id,
                                                 'time': time,
                                                 'unit': unit,
                                                 'text': text,
                                                 'email': email,
                                                 'user': user});
              user_alert_conf.$save({'siteId':SITE_ID}, function(data){
                  console.log('success');
                  alert('success!');
              });
          }
    }


 AlertConfController.$inject = ['AlertConf', '$compile', '$configService', '$scope'];
