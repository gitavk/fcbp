(function () {
  'use strict';

  angular
    .module('fcbp.common.routes', ['ngRoute']);
    
  angular
    .module('fcbp.common.routes')
    .config(config);

  config.$inject = ['$routeProvider'];

  /**
  * @name config
  * @desc Define valid application routes
  */
  function config($routeProvider) {
    $routeProvider.when('/login', {
      controller: 'LoginController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/login.html'
    }).when('/clients', {
      controller: 'ClientsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/clients.html'
    }).when('/advance_search', {
      controller: 'AdvanceSearchController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/advance_search.html'
    }).when('/new-client', {
      controller: 'NewClientController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/new-client.html'
    }).when('/edit-client/:uid', {
      controller: 'EditClientController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/edit-client.html'
    }).when('/photo-client/:uid', {
      controller: 'PhotoClientController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/photo-client.html'
    }).when('/new-client-product/:uid', {
      controller: 'NewClientProductController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/new-client-product.html'
    }).when('/client-introductory/:uid', {
      controller: 'ClientIntroductoryController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/introductory.html'
    }).when('/cardclient/:uid', {
      controller: 'ClientCardController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/card-client.html'
    }).when('/employees', {
      controller: 'EmployeesController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/employees/employees.html'
    }).when('/positions', {
      controller: 'PositionsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/employees/positions.html'
    }).when('/new-employee', {
      controller: 'NewEmployeeController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/employees/new-employee.html'
    }).when('/edit-employee/:uid', {
      controller: 'NewEmployeeController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/employees/new-employee.html'
    }).when('/employees-list', {
      controller: 'EmployeesListController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/employees/employees-list.html'
    }).when('/usecardclient/:uid', {
      controller: 'UseClientCardController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/clubcard.html'
    }).when('/editvisit/:uid', {
      controller: 'EditVisitController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/edit_visit.html'
    }).when('/editvisit_personal/:uid', {
      controller: 'EditVisitPersonalController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/edit_visit_personal.html'
    }).when('/useaquaaerobics/:uid', {
      controller: 'UseClientAquaController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/aquaaerobics.html'
    }).when('/useticket/:uid', {
      controller: 'UseClientTicketController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/ticket.html'
    }).when('/usepersonal/:uid', {
      controller: 'UseClientPersonalController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/personal.html'
    }).when('/usetiming/:uid', {
      controller: 'UseTimingController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/use/timing.html'
    }).when('/', {
      controller: 'StartController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/index.html'
    })
    .otherwise('/');
  }
})();