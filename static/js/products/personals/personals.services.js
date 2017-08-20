/**
* Personals
* @namespace fcbp.layout.services
*/
(function () {
  'use strict';

  angular
    .module('fcbp.layout.services')
    .factory('Personals', Personals);

  Personals.$inject = ['$http'];

  /**
  * @namespace Personals
  * @returns {Factory}
  */
  function Personals($http) {
    /**
    * @name Personals
    * @desc The Factory to be returned
    */
    var Personals = {
      create: create,
      list: list,
      get: get,
      update: update,
      use: use,
      use_exit: use_exit,
      active: active,
      active_list: active_list,
      prolongation: prolongation,
      prolongation_del: prolongation_del,
      ownerp: ownerp,
    };

    return Personals;

    ////////////////////
    /**
    * @name create
    * @desc Create a new Personal
    * @param {form data} by models of the new Personal
    * @returns {Promise}
    * @memberOf fcbp.personals.services.Personals
    */
    function create(fdata) {
      return $http.post('/api/v1/products/personal/', fdata
                        ).error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }
    /**
    **/
    function list() {
      return $http.get('/api/v1/products/personal/')
    }

    function active_list() {
      return $http.get('/api/v1/products/personal/active_list/')
    }

    function get(uid) {
      return $http.get('/api/v1/clients/personal/' + uid + '/')
    }

    function update(uid, fdata) {
      return $http.put('/api/v1/products/personal/' + uid + '/', fdata)
    }

    function active(uid) {
      return $http.post('/api/v1/products/personal/' + uid + '/active/')
    }

    function use(fdata) {
      return $http.post('/api/v1/clients/usepersonal/', fdata)
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function use_exit(fdata) {
      return $http.post('/api/v1/clients/usepersonal/exit/', fdata)
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function prolongation(fdata) {
      return $http.post('/api/v1/clients/prolongationticket_personal/',  fdata)
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function prolongation_del(uid) {
      return $http.delete('/api/v1/clients/prolongationticket_personal/' + uid + '/')
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function ownerp(fdata) {
      return $http.post('/api/v1/clients/ownerp/', fdata)
    }

  }

})();