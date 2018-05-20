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
      use_get: use_get,
      use_update: use_update,
      use_del: use_del,
      use_exit: use_exit,
      active: active,
      active_list: active_list,
      prolongation: prolongation,
      prolongation_del: prolongation_del,
      similar: similar,
      ownerp: ownerp,
      add_extra: add_extra,
      archive_client_list: archive_client_list,
      archive_reopen: archive_reopen,
      archive_purge_credits: archive_purge_credits
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

    function archive_client_list(uid) {
      return $http.get('/api/v1/clients/archive/personal/'+ uid + '/client/')
    }

    function update(uid, fdata) {
      return $http.put('/api/v1/products/personal/' + uid + '/', fdata)
    }

    function active(uid) {
      return $http.post('/api/v1/products/personal/' + uid + '/active/')
    }

    function add_extra(uid, fdata) {
      return $http.post('/api/v1/clients/personal/' + uid + '/add_extra/', fdata)
    }

    function use(fdata) {
      return $http.post('/api/v1/clients/usepersonal/', fdata)
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function use_get(uid) {
      return $http.get('/api/v1/clients/usepersonal/' + uid + '/')
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function use_update(uid, fdata) {
      return $http.put('/api/v1/clients/usepersonal/' + uid + '/',  fdata)
                  .error(function(data, status, headers, config) {
                          console.log(data)
                        });
    }

    function use_del(uid) {
      return $http.delete('/api/v1/clients/usepersonal/' + uid + '/')
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
      return $http.post('/api/v1/clients/prolongationticket_personal/', fdata)
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

    function similar(uid) {
      return $http.get('/api/v1/clients/personal/' + uid + '/similar/')
    }

    function ownerp(fdata) {
      return $http.post('/api/v1/clients/ownerp/', fdata)
    }

    function archive_reopen(uid) {
      return $http.post('/api/v1/clients/archive/personal/'+ uid + '/reopen/')
    }

    function archive_purge_credits(uid) {
      return $http.post('/api/v1/clients/archive/personal/'+ uid + '/purge_credits/')
    }

  }

})();