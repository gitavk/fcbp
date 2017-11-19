/**
* EditVisitController
* @namespace fcbp.clients.controllers
*/
(function () {
  'use strict';

  angular
    .module('fcbp.clients.controllers')
    .controller('EditVisitController', EditVisitController);

  EditVisitController.$inject = ['$location', '$rootScope', '$routeParams',
                                     '$route', '$scope', '$http', 'ClientPayment',
                                     'ClientCredit', 'ClubCard', 'Employees', 'Training'];

  /**
  * @namespace EditVisitController
  */
  function EditVisitController($location, $rootScope, $routeParams,
                                   $route, $scope, $http, ClientPayment,
                                   ClientCredit, ClubCard, Employees, Training) {
    var vm = this;

    vm.error = '';

    vm.uid = $routeParams.uid

    // vm.update_date_begin = update_date_begin;
    vm.add_train = add_train;
    vm.rm_train = rm_train;
    vm.use_update = use_update;
    // vm.use_trainings = [];

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf fcbp.clubcard.controllers.NewClubCardController
    */
    function activate() {

      ClubCard.use_get(vm.uid).then(getTrainingSuccessFn, getTrainingErrorFn);

      /**
      * @name getTrainingSuccessFn
      * @desc Show snackbar with success message
      */
      function getTrainingSuccessFn(data, status, headers, config) {
        vm.train = data.data;
        console.log(vm.train.date)
        vm.train.date = moment(vm.train.date, 'YYYY-MM-DD HH:mm').format('DD.MM.YYYY HH:mm')
        if (vm.train.end) {
          vm.train.end = moment(vm.train.end, 'YYYY-MM-DD HH:mm').format('HH:mm')
        }
      }

      /**
      * @name getTrainingErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function getTrainingErrorFn(data, status, headers, config) {
        console.log(data)
      }

      Training.active_list().then(listTrainingSuccessFn, listTrainingErrorFn);
    
      /**
      * @name listTrainingSuccessFn
      * @desc Show snackbar with success message
      */
      function listTrainingSuccessFn(data, status, headers, config) {
        vm.trainings = data.data;
        console.log(data.data)
      }

      /**
      * @name listTrainingErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function listTrainingErrorFn(data, status, headers, config) {
        console.log(data)
      }

    }

    function add_train(key) {
      vm.train.clubcardtrains_set.push({
        'name': vm.trainings[key].name, 'training': vm.trainings[key].id});
    }

    function rm_train(key) {
      vm.train.clubcardtrains_set.splice(key, 1);
    }

    function use_update() {
      if (vm.train.end) {
        var hh = moment(vm.train.end, 'HH:mm').hours()
        var mm = moment(vm.train.end, 'HH:mm').minutes()
        vm.train.end = moment(vm.train.date, 'DD.MM.YYYY hh:mm');
        vm.train.end = vm.train.end.minute(mm);
        vm.train.end = vm.train.end.hour(hh);
        vm.train.end = vm.train.end.format('DD.MM.YYYY HH:mm');
      }
      ClubCard.use_update(vm.uid, vm.train).then(updateTrainingSuccessFn, updateTrainingErrorFn);

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
    }

  };

})();