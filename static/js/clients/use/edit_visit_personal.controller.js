/**
* EditVisitPersonalController
* @namespace fcbp.clients.controllers
*/
(function () {
  'use strict';

  angular
    .module('fcbp.clients.controllers')
    .controller('EditVisitPersonalController', EditVisitPersonalController);

  EditVisitPersonalController.$inject = ['$location', '$rootScope', '$routeParams',
                                     '$route', '$scope', '$http', 'ClientPayment',
                                     'Personals', 'Employees'];

  /**
  * @namespace EditVisitPersonalController
  */
  function EditVisitPersonalController($location, $rootScope, $routeParams,
                                   $route, $scope, $http, ClientPayment,
                                   Personals, Employees) {
    var vm = this;

    vm.error = '';
    vm.uid = $routeParams.uid
    vm.use_update = use_update;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf fcbp.clubcard.controllers.EditVisitPersonalController
    */
    function activate() {

      Personals.use_get(vm.uid).then(getTrainingSuccessFn, getTrainingErrorFn);
      /**
      * @name getTrainingSuccessFn
      * @desc Show snackbar with success message
      */
      function getTrainingSuccessFn(data, status, headers, config) {
        vm.train = data.data;
        vm.train.date = moment(vm.train.date, 'YYYY-MM-DD HH:mm').format('DD.MM.YYYY HH:mm')
        if (vm.train.end) {
          vm.train.end = moment(vm.train.end, 'YYYY-MM-DD HH:mm').format('HH:mm')
        }

        vm.emp_filter = {positions: vm.train.positions }
        Employees.personal_trainers(vm.emp_filter).then(listEmployeeSuccessFn, listEmployeeErrorFn);
        /**
        * @name listEmployeeSuccessFn
        * @desc Show snackbar with success message
        */
        function listEmployeeSuccessFn(data, status, headers, config) {
          vm.employees = data.data;
        }
        /**
        * @name listEmployeeErrorFn
        * @desc Propogate error event and show snackbar with error message
        */
        function listEmployeeErrorFn(data, status, headers, config) {
          console.log(data)
        };
      }

      /**
      * @name getTrainingErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function getTrainingErrorFn(data, status, headers, config) {
        console.log(data)
      };

    }; // End activate

    function use_update() {
      if (vm.train.end) {
        var hh = moment(vm.train.end, 'HH:mm').hours()
        var mm = moment(vm.train.end, 'HH:mm').minutes()
        vm.train.end = moment(vm.train.date, 'DD.MM.YYYY hh:mm');
        vm.train.end = vm.train.end.minute(mm);
        vm.train.end = vm.train.end.hour(hh);
        vm.train.end = vm.train.end.format('DD.MM.YYYY HH:mm');
      }
      Personals.use_update(vm.uid, vm.train).then(updateTrainingSuccessFn, updateTrainingErrorFn);

      /**
      * @name updateTrainingSuccessFn
      * @desc Show snackbar with success message
      */
      function updateTrainingSuccessFn(data, status, headers, config) {
        activate();
      }

      /**
      * @name updateTrainingErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function updateTrainingErrorFn(data, status, headers, config) {
        console.log(data)
      }
    }; // End use update

  };

})();