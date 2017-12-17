/**
* UseClientCardController
* @namespace fcbp.clients.controllers
*/
(function () {
  'use strict';

  angular
    .module('fcbp.clients.controllers')
    .controller('UseClientCardController', UseClientCardController);

  UseClientCardController.$inject = ['$location', '$rootScope', '$routeParams',
                                     '$route', '$scope', '$http', 'Clients', 'ClientPayment',
                                     'ClientCredit', 'ClubCard', 'Employees', 'Training'];

  /**
  * @namespace UseClientCardController
  */
  function UseClientCardController($location, $rootScope, $routeParams,
                                   $route, $scope, $http, Clients, ClientPayment,
                                   ClientCredit, ClubCard, Employees, Training) {
    var vm = this;

    vm.use = use;
    vm.use_del = use_del;
    vm.error = '';

    vm.uid = $routeParams.uid

    vm.valid_freeze_date = true;

    vm.guest = guest;
    vm.personal = personal;
    vm.fitness = fitness;
    vm.freeze = freeze;
    vm.freeze_chg = freeze_chg;
    vm.freeze_del = freeze_del;
    vm.paid_activate = paid_activate;
    vm.to_archive = to_archive;
    vm.update_date_begin = update_date_begin;
    vm.activation = activation;
    vm.update_type = update_type;
    vm.add_train = add_train;
    vm.rm_train = rm_train;
    vm.use_trainings = [];
    vm.payment = payment;
    vm.day_change = day_change;
    vm.cr_split = cr_split;

    vm.prolongation = prolongation;
    vm.prolongation_del = prolongation_del;
    vm.is_paid = is_paid;
    vm.search_client = search_client;
    vm.choose_owner = choose_owner;
    vm.set_owner = set_owner;

    vm.reopen = reopen;
    vm.archive_purge_credits = archive_purge_credits;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf fcbp.clubcard.controllers.NewClubCardController
    */
    function activate() {
      var now = moment().format('DD.MM.YYYY HH:mm')
      // forms data initial
      vm.prdata = {
        days: 1,
        amount: 0.0,
        is_paid: false,
        client_club_card: vm.uid,
        date: now,
        payment_type: 1
      }
      // freeze data
      vm.frdata = {
        days: 1,
        amount: 0.0,
        is_paid: false,
        client_club_card: vm.uid,
        fdate: moment().format('DD.MM.YYYY'),
        tdate: moment().format('DD.MM.YYYY'),
        is_credit: false,
        payment_type: 1
      }
      //  paid activate data
      vm.padata = {
        is_paid_activate: true,
        paid_activate_amount: 0,
        payment_type: 1
      }
      //  to archive data
      vm.ardata = {
        status: 0,
        block_comment: ''
      }

      vm.pdata = {
        client_club_card: vm.uid,
        date: now
      }

      vm.fitdata = {
        client_club_card: vm.uid,
        date: now
      }

      vm.new_type = {
        amount: 0,
        date: moment().format('DD.MM.YYYY')
      }

      vm.owner = {
        amount: 0,
        payment_type: 0
      }
      // end forms


      ClubCard.get(vm.uid).then(cardclientSuccessFn, cardclientErrorFn);

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function cardclientSuccessFn(data, status, headers, config) {
        vm.card = data.data;
        if (vm.card.date_begin) {
          // update date begin data
          vm.new_date = {
            date_begin: moment(vm.card.date_begin, 'YYYY-MM-DD').format('DD.MM.YYYY'),
          }
        }

        if (vm.card.status == 2) {
          // activation data
          vm.activation_data = { date_begin: moment().format('DD.MM.YYYY'), }
        }

        if (vm.card.rest_freeze > 0 && vm.card.rest_freeze_times > 0) {
          vm.free_freeze = true
        } else {
          vm.free_freeze = false
          vm.frdata.is_paid = true
        }
        // is free prolongation
        if (vm.card.rest_prolongation > 0) {
          vm.free_prolongation = true
        } else {
          vm.free_prolongation = false
          vm.prdata.is_paid = true
        }
        // for edit personalclubcard
        if (vm.card.personalclubcard_set.length) {
          var p_data = vm.card.personalclubcard_set[0]
          vm.pdata = p_data
          vm.pdata['date'] = moment(p_data.date, 'YYYY-MM-DD HH:mm').format('DD.MM.YYYY HH:mm')
        }
        // for edit fitnessclubcard_set
        if (vm.card.fitnessclubcard_set.length) {
          var f_data = vm.card.fitnessclubcard_set[0]
          vm.fitdata = f_data
          vm.fitdata['date'] = moment(f_data.date, 'YYYY-MM-DD HH:mm').format('DD.MM.YYYY HH:mm')
        }
        // for edit credit_set date
        angular.forEach(vm.card.credit_set, function (value, key) {
          value.schedule = moment(value.schedule, 'YYYY-MM-DD').format('DD.MM.YYYY');
        });
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function cardclientErrorFn(data, status, headers, config) {
        console.log(data);
      }

      Employees.list().then(listEmployeeSuccessFn, listEmployeeErrorFn);
    
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
      }

      Training.active_list().then(listTrainingSuccessFn, listTrainingErrorFn);
    
      /**
      * @name listTrainingSuccessFn
      * @desc Show snackbar with success message
      */
      function listTrainingSuccessFn(data, status, headers, config) {
        vm.trainings = data.data;
      }


      /**
      * @name listTrainingErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function listTrainingErrorFn(data, status, headers, config) {
        console.log(data)
      }

      ClubCard.similar(vm.uid).then(listSimilarSuccessFn, listSimilarErrorFn);

      /**
      * @name listSimilarSuccessFn
      * @desc Show snackbar with success message
      */
      function listSimilarSuccessFn(data, status, headers, config) {
        vm.similar = data.data;
        console.log(vm.similar)
      }


      /**
      * @name listSimilarErrorFn
      * @desc Propogate error event and show snackbar with error message
      */
      function listSimilarErrorFn(data, status, headers, config) {
        console.log(data)
      }

    }

    function use(out) {

      var uid = $routeParams.uid
      var fdata = {client_club_card: uid, trainings: vm.use_trainings }

      if (out) {
        ClubCard.use_exit(fdata).then(cardclientSuccessFn, cardclientErrorFn);
        return 1
      }

      ClubCard.use(fdata).then(cardclientSuccessFn, cardclientErrorFn);

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function cardclientSuccessFn(data, status, headers, config) {
        if ('error' in data.data) {
          vm.error = data.data['error']
        } else {
          activate();
          console.log('success')
        }
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function cardclientErrorFn(data, status, headers, config) {
        console.log(data);
      }

    }

    function use_del(uid) {
      ClubCard.use_del(uid).then(useSuccessFn, useErrorFn);
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
    }

    function guest() {
      var numberPattern = /\d+/g;

      if (vm.fguest.mobile_form) {
        var phone = vm.fguest.mobile_form.match( numberPattern );
        vm.fguest.phone = phone.join("");
      } else {
        delete vm.fguest.phone
      }
      
      ClubCard.guest(vm.uid, vm.fguest).then(cardclientSuccessFn, cardclientErrorFn);

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function cardclientSuccessFn(data, status, headers, config) {
        console.log(data);
        vm.fguest = {};
        activate();
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function cardclientErrorFn(data, status, headers, config) {
        console.log(data);
      }

    }

    function add_train(key) {
      vm.use_trainings.push({'name': vm.trainings[key].name,
                             'id': vm.trainings[key].id
                            });
    }

    function rm_train(key) {
      vm.use_trainings.splice(key, 1);
    }

    function personal() {
      ClubCard.personal(vm.pdata).then(cardclientSuccessFn, cardclientErrorFn);

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function cardclientSuccessFn(data, status, headers, config) {
        vm.pdata = {client_club_card: vm.uid,};
        activate();
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function cardclientErrorFn(data, status, headers, config) {
        console.log(data);
      }

    }

    function fitness() {
      ClubCard.fitness(vm.fitdata).then(cardclientSuccessFn, cardclientErrorFn);

      /**
      * @name cardclientSuccessFn
      * @desc Update ClubCard array on view
      */
      function cardclientSuccessFn(data, status, headers, config) {
        vm.fitdata = {client_club_card: vm.uid,};
        activate();
      }

      /**
      * @name cardclientErrorFn
      * @desc console log error
      */
      function cardclientErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

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

      ClubCard.prolongation(vm.prdata).then(prolongationSuccessFn, prolongationErrorFn);

      /**
      * @name prolongationSuccessFn
      * @desc Update ClubCard array on view
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

    }

    function prolongation_del(uid) {
      ClubCard.prolongation_del(uid).then(prolongationSuccessFn, prolongationErrorFn);

      /**
      * @name prolongationSuccessFn
      * @desc Update ClubCard array on view
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

    }

    function is_paid() {
      if (!vm.prdata.is_paid) {
        vm.prdata.amount = 0;
      }

      if (!vm.frdata.is_paid) {
        vm.frdata.amount = 0;
        if (vm.frdata.days > vm.card.rest_freeze) {
          vm.frdata.err = 'Недопустимое количество дней заморозки'
        } else {
          vm.frdata.err = ''
        }
      } else if (vm.frdata.days > 0) {
        vm.frdata.err = ''
      }

    }

    function freeze(is_extra) {

      if (is_extra == 'is_extra') {
        if (!vm.frdata.note) {
          vm.frdata.err = 'Поле примечание должно содеражть не менее 3 символов'
          return
        }
        vm.frdata.is_paid = false
        vm.frdata.amount = 0
        vm.frdata.is_extra = true
      }

      if ( vm.frdata.is_credit ) {
        var credit_date = moment().add(1, 'days').startOf('day').format('DD.MM.YYYY');
        vm.frdata.schedule = credit_date;
        vm.frdata.discount = 0;
        vm.frdata.count = 1;
      }

      ClubCard.freeze(vm.uid, vm.frdata).then(freezeSuccessFn, freezeErrorFn);

      /**
      * @name freezeSuccessFn
      * @desc Update ClubCard array on view
      */
      function freezeSuccessFn(data, status, headers, config) {
        activate();
      }

      /**
      * @name freezeErrorFn
      * @desc console log error
      */
      function freezeErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    function freeze_chg(field) {
      if (field == 'days') {
        var tdate = moment(vm.frdata.fdate, 'DD.MM.YYYY').add(vm.frdata.days - 1, 'days')
        vm.frdata.tdate = tdate.format('DD.MM.YYYY')
      } else if (field == 'fdate' || field == 'tdate') {
        var fdate = moment(vm.frdata.fdate, 'DD.MM.YYYY')
        var tdate = moment(vm.frdata.tdate, 'DD.MM.YYYY')
        vm.frdata.days = tdate.diff(fdate, 'days') + 1
      }
      if (!vm.frdata.is_paid && vm.frdata.days > vm.card.rest_freeze) {
          vm.frdata.err = 'Недопустимое количество дней заморозки'
        } else if (vm.frdata.days < 1) {
        vm.frdata.err = 'Неверные значения дат'
      } else {
        vm.frdata.err = ''
      }
    }


    function freeze_del(uid) {
      ClubCard.freeze_del(uid).then(prolongationSuccessFn, prolongationErrorFn);

      /**
      * @name prolongationSuccessFn
      * @desc Update ClubCard array on view
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

    }

    function paid_activate() {

      $http.put('/api/v1/clients/clubcard/' + vm.uid + '/', vm.padata
                ).then(paid_activateSuccessFn, paid_activateErrorFn);

      /**
      * @name paid_activateSuccessFn
      * @desc Update ClubCard array on view
      */
      function paid_activateSuccessFn(data, status, headers, config) {
        console.log(data);
        activate();
      }

      /**
      * @name paid_activateErrorFn
      * @desc console log error
      */
      function paid_activateErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    function to_archive() {
      $http.put('/api/v1/clients/clubcard/' + vm.uid + '/', vm.ardata
                ).then(to_archiveSuccessFn, to_archiveErrorFn);

      /**
      * @name to_archiveSuccessFn
      * @desc Update ClubCard array on view
      */
      function to_archiveSuccessFn(data, status, headers, config) {
        window.location = '/#/archive/clubcard/' + vm.uid
      }

      /**
      * @name to_archiveErrorFn
      * @desc console log error
      */
      function to_archiveErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    function update_date_begin() {
      vm.new_date.update_success = false
      vm.new_date.update_error = false
      $http.put('/api/v1/clients/clubcard/' + vm.uid + '/', vm.new_date
                ).then(update_date_beginSuccessFn, update_date_beginErrorFn);

      /**
      * @name update_date_beginSuccessFn
      * @desc Update ClubCard on view
      */
      function update_date_beginSuccessFn(data, status, headers, config) {
         $route.reload();
      }

      /**
      * @name update_date_beginErrorFn
      * @desc console log error
      */
      function update_date_beginErrorFn(data, status, headers, config) {
        console.log(data)
        vm.new_date.update_error = data.data['date_begin'][0];
      }
    };

    // manual activation 
    function activation() {
      vm.activation_data['update_success'] = false
      var date_begin = moment(vm.activation_data.date_begin, 'DD.MM.YYYY').format('YYYY-MM-DD')
      vm.activation_data.date_begin = date_begin
      $http.post('/api/v1/clients/clubcard/' + vm.uid + '/activation/', vm.activation_data
                ).then(activationSuccessFn, activationErrorFn);

      /**
      * @name activationSuccessFn
      * @desc Update ClubCard on view
      */
      function activationSuccessFn(data, status, headers, config) {
        $route.reload();
      }

      /**
      * @name activationErrorFn
      * @desc console log error
      */
      function activationErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    $scope.$watch('vm.new_type.club_card', function(id){
      angular.forEach(vm.similar, function(attr){
        if(attr.id === id){
          vm.new_type.amount = attr.price - vm.card.price;
        }
      });
    });

    // manual update_type 
    function update_type() {
      $http.post('/api/v1/clients/clubcard/' + vm.uid + '/new_type/', vm.new_type
                ).then(activationSuccessFn, activationErrorFn);

      /**
      * @name activationSuccessFn
      * @desc Update ClubCard on view
      */
      function activationSuccessFn(data, status, headers, config) {
        $route.reload();
      }

      /**
      * @name activationErrorFn
      * @desc console log error
      */
      function activationErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // function for close credit
    function payment(payment_type, uid) {
      ClientPayment.close_credit(payment_type, uid)
                   .then(closeSuccessFn, closeErrorFn);

      /**
      * @name closeSuccessFn
      * @desc Update ClubCard array on view
      */
      function closeSuccessFn(data, status, headers, config) {
        console.log('success')
        activate()
      }

      /**
      * @name closeErrorFn
      * @desc console log error
      */
      function closeErrorFn(data, status, headers, config) {
        console.log(data);
      }

    };

    // function for update date of the credit
    function day_change(cr) {
      var fdata = {'schedule': cr.schedule}
      ClientCredit.update(cr.id, fdata).then(CrUpdSuccessFn, CrUpdErrorFn);

      /**
      * @name CrUpdSuccessFn
      * @desc Update ClubCard array on view
      */
      function CrUpdSuccessFn(data, status, headers, config) {
        console.log('success')
        activate()
      }

      /**
      * @name CrUpdErrorFn
      * @desc console log error
      */
      function CrUpdErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // function for split amount of the credit
    function cr_split(cr) {
      var fdata = {'amount': cr.amount}
      ClientCredit.update(cr.id, fdata).then(CrUpdSuccessFn, CrUpdErrorFn);

      /**
      * @name CrUpdSuccessFn
      * @desc Update ClubCard array on view
      */
      function CrUpdSuccessFn(data, status, headers, config) {
        activate()
      }

      /**
      * @name CrUpdErrorFn
      * @desc console log error
      */
      function CrUpdErrorFn(data, status, headers, config) {
        console.log(data);
      }
    };

    // reopen old card
    function reopen() {
      ClubCard.archive_reopen(vm.uid).then(reopenSuccessFn, reopenErrorFn);

      /**
      * @name reopenSuccessFn
      * @desc Update ClubCard array on view
      */
      function reopenSuccessFn(data, status, headers, config) {
        window.location = '/#/usecardclient/' + vm.uid
      }

      /**
      * @name reopenErrorFn
      * @desc console log error
      */
      function reopenErrorFn(data, status, headers, config) {
        console.log(data);
      };
    };

    // purge credits for old card
    function archive_purge_credits() {
      ClubCard.archive_purge_credits(vm.uid).then(purgeSuccessFn, purgeErrorFn);

      /**
      * @name purgeSuccessFn
      * @desc Update ClubCard array on view
      */
      function purgeSuccessFn(data, status, headers, config) {
        activate()
      };

      /**
      * @name purgeErrorFn
      * @desc console log error
      */
      function purgeErrorFn(data, status, headers, config) {
        console.log(data);
      };
    };

    /* Search new owners clients
    */
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
    function choose_owner(key) {
      vm.new_owner = vm.findClients[key];
      vm.findClients = [];
    }

    /*
    * Set new owner
    */
    function set_owner() {
      ClubCard.ownercc({
        "client": vm.new_owner.id,
        "club_card": vm.uid,
        "amount": vm.owner.amount,
        "payment_type": vm.owner.payment_type
      }).then(clntSetOwnerSuccessFn, clntSetOwnerErrorFn);

      function clntSetOwnerSuccessFn(data, status, headers, config) {
         $location.url('/cardclient/' + vm.new_owner.id);
      }

      function clntSetOwnerErrorFn(data, status, headers, config) {
        console.log(data);
      }

    }

  };

})();