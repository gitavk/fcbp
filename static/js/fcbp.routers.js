(function () {
  'use strict';

  angular
    .module('fcbp.routes', ['ngRoute']);
    
  angular
    .module('fcbp.routes')
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
    }).when('/products', {
      controller: 'ProductsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/products.html'
    }).when('/periods', {
      controller: 'PeriodsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/periods.html'
    }).when('/clubcards', {
      controller: 'ClubCardsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/clubcards.html'
    }).when('/aqua-aerobics', {
      controller: 'AquaAerobicsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/aqua-aerobicses.html'
    }).when('/sports', {
      controller: 'SportsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/sports.html'
    }).when('/tickets', {
      controller: 'TicketsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/tickets.html'
    }).when('/personals', {
      controller: 'PersonalsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/products/personals.html'
    }).when('/clients', {
      controller: 'ClientsController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/clients.html'
    }).when('/new-client', {
      controller: 'NewClientController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/new-client.html'
    }).when('/new-client-product/:uid', {
      controller: 'NewClientProductController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/clients/new-client-product.html'
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
    }).when('/', {
      controller: 'StartController',
      controllerAs: 'vm',
      templateUrl: '/static/templates/index.html'
    }).otherwise('/');
  }
})();