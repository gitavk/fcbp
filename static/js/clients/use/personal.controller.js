/**
* UseClientPersonalController
* @namespace fcbp.clients.controllers
*/
(function () {
  'use strict';

  angular
    .module('fcbp.clients.controllers')
    .controller('UseClientPersonalController', UseClientPersonalController);

  UseClientPersonalController.$inject = [
    '$location', '$rootScope', '$routeParams', '$scope', '$http',
    'Personals', 'Employees', 'Clients'];

  /**
  * @namespace UseClientPersonalController
  */
  function UseClientPersonalController(
    $location, $rootScope, $routeParams, $scope, $http,
    Personals, Employees, Clients) {

    var vm = this;

    vm.use = use;
    vm.use_del = use_del;
    vm.set_emp = set_emp;
    vm.prolongation = prolongation;
    vm.prolongation_del = prolongation_del;

    vm.search_client = search_client;
    vm.choose_owner = choose_owner;
    vm.set_owner = set_owner;
    vm.update_date_begin = update_date_begin;
    vm.add_extra = add_extra;
    vm.to_archive = to_archive;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf fcbp.clients.controllers.UseClientPersonalController
    */
    function activate() {
      vm.uid = $routeParams.uid;

      var now = moment().format('DD.MM.YYYY HH:mm')
      // forms data initial
      vm.prdata = {
        days: 1,
        amount: 0.0,
        is_paid: false,
        personal: vm.uid,
        date: now,
        payment_type: 1
      }

      vm.owner = {
        amount: 0,
        payment_type: 0
      }

      Personals.get(vm.uid).then(personalclientSuccessFn, personalclientErrorFn);

      /**
      * @name personalclientSuccessFn
      * @desc Update Personals array on view
      */
      function personalclientSuccessFn(data, status, headers, config) {
        vm.personal = data.data;
        vm.emp_filter = {positions: vm.personal.positions }
        // is free prolongation
        if (vm.personal.rest_prolongation > 0) {
          vm.free_prolongation = true
        } else {
          vm.free_prolongation = false
          vm.prdata.is_paid = true
        }

        if (vm.personal.date_begin) {
          // update date begin data
          vm.new_date = {
            date_begin: moment(vm.personal.date_begin, 'YYYY-MM-DD').format('DD.MM.YYYY'),
          }
        }

        vm.udata = {
          instructor: vm.personal.instructor,
          client_personal: vm.uid
        }

        // to archive data
        vm.ardata = {
          status: 0,
          block_comment: ''
        }

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

      };
      /**
      * @name personalclientErrorFn
      * @desc console log error
      */
      function personalclientErrorFn(data, status, headers, config) {
        console.log(data);
      }
    }; // end activate

    function set_emp() {
      $http.patch('/api/v1/clients/personal/' + vm.uid + '/', vm.empdata
                ).then(set_empSuccessFn, set_empErrorFn);;

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function set_empSuccessFn(data, status, headers, config) {
        activate();
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function set_empErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    /* Search new owners clients */
    function search_client() {
      vm.new_owner = ""
      Clients.full_search(vm.ext).then(clntSearchSuccessFn, clntSearchErrorFn);

      function clntSearchSuccessFn(data, status, headers, config) {
          vm.findClients = data.data;
          console.log(data)
      }

      function clntSearchErrorFn(data, status, headers, config) {
          console.log(data);
      }
    };

    /*
    * Choose new owner
    */
    function choose_owner(key, extra) {
      if (extra) {
        vm.new_extra = vm.findClients[key];
      } else {
        vm.new_owner = vm.findClients[key];
      }
      vm.findClients = [];
    }

    /* Set new owner */
    function set_owner() {
      Personals.ownerp({
        "client": vm.new_owner.id,
        "personal": vm.uid,
        "amount": vm.owner.amount,
        "payment_type": vm.owner.payment_type
      }).then(clntSetOwnerSuccessFn, clntSetOwnerErrorFn);

      function clntSetOwnerSuccessFn(data, status, headers, config) {
         $location.url('/cardclient/' + vm.new_owner.id);
      }

      function clntSetOwnerErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // add extra clients to the personal
    function add_extra() {
      Personals.add_extra(vm.uid, {
        "extra_client": vm.new_extra.id,
      }).then(clntAddExtraSuccessFn, clntAddExtraErrorFn);
      function clntAddExtraSuccessFn(data, status, headers, config) {
        activate();
      }
      function clntAddExtraErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // Add prolongation record
    function prolongation(is_extra) {
      if (is_extra == 'is_extra') {
        if (!vm.prdata.note) {
          vm.prdata.err = 'Поле примечание должно содеражть не менее 3 символов'
          return
        }
        vm.prdata.is_paid = false
        vm.prdata.amount = 0
        vm.prdata.is_extra = true
      }
      Personals.prolongation(vm.prdata).then(prolongationSuccessFn, prolongationErrorFn);
      /**
      * @name prolongationSuccessFn
      * @desc Update Personals array on view
      */
      function prolongationSuccessFn(data, status, headers, config) {
        activate();
      }

      /**
      * @name prolongationErrorFn
      * @desc console log error
      */
      function prolongationErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };
    // Remove prolongation record
    function prolongation_del(uid) {
      Personals.prolongation_del(uid).then(prolongationSuccessFn, prolongationErrorFn);
      /**
      * @name prolongationSuccessFn
      * @desc Update Personals array on view
      */
      function prolongationSuccessFn(data, status, headers, config) {
        activate();
      }
      /**
      * @name prolongationErrorFn
      * @desc console log error
      */
      function prolongationErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // Add new visit
    function use(out) {
      if (out) {
        Personals.use_exit(vm.udata).then(personalclientSuccessFn, personalclientErrorFn);
        return 1
      }
      Personals.use(vm.udata).then(personalclientSuccessFn, personalclientErrorFn);
      /**
      * @name personalclientSuccessFn
      * @desc Update Personals array on view
      */
      function personalclientSuccessFn(data, status, headers, config) {
        activate();
        console.log('success')
      }
      /**
      * @name personalclientErrorFn
      * @desc console log error
      */
      function personalclientErrorFn(data, status, headers, config) {
        console.log(data);
      }
    }; // End function use

    // Remove visit
    function use_del(uid) {
      Personals.use_del(uid).then(useSuccessFn, useErrorFn);
      /**
      * @name useSuccessFn
      * @desc Update ClubCard array on view
      */
      function useSuccessFn(data, status, headers, config) {
        activate();
      }
      /**
      * @name useErrorFn
      * @desc console log error
      */
      function useErrorFn(data, status, headers, config) {
        console.log(data);
      }
    }; // End remove visit

    // Deactivate
    function to_archive() {
      $http.patch('/api/v1/clients/personal/' + vm.uid + '/', vm.ardata
                ).then(to_archiveSuccessFn, to_archiveErrorFn);

      /**
      * @name to_archiveSuccessFn
      * @desc Update ClubCard array on view
      */
      function to_archiveSuccessFn(data, status, headers, config) {
        window.location = '/#/archive/personal/' + vm.uid
      }

      /**
      * @name to_archiveErrorFn
      * @desc console log error
      */
      function to_archiveErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // Function update_date_begin
    function update_date_begin() {
      vm.new_date.update_success = false
      vm.new_date.update_error = false
      $http.patch('/api/v1/clients/personal/' + vm.uid + '/', vm.new_date
                ).then(update_date_beginSuccessFn, update_date_beginErrorFn);

      /**
      * @name update_date_beginSuccessFn
      * @desc Update ClubCard on view
      */
      function update_date_beginSuccessFn(data, status, headers, config) {
        activate();
      }
      /**
      * @name update_date_beginErrorFn
      * @desc console log error
      */
      function update_date_beginErrorFn(data, status, headers, config) {
        console.log(data)
        vm.new_date.update_error = data.data['date_begin'][0];
      }
    }; // END function update_date_begin

  };

})();