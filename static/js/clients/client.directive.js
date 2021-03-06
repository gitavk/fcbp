/**
* Client
* @namespace fcbp.client.directives
*/
(function () {
  'use strict';

  angular
    .module('fcbp.client.directives')
    .directive('client', client);

  /**
  * @namespace Client
  */
  function client() {
    /**
    * @name directive
    * @desc The directive to be returned
    * @memberOf fcbp.client.directives.Client
    */
    var directive = {
      restrict: 'E',
      scope: {
        client: '='
      },
      templateUrl: '/static/templates/clients/client.html?112'
    };

    return directive;
  }
})();