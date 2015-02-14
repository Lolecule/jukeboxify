'use strict';

var jukeboxifyServices = angular.module('jukeboxifyServices', ['ngResource'])

jukeboxifyServices.factory('Spotify', ['$resource',
  function($resource) {
    return $resource('https://api.spotify.com/v1/search', {}, {
      search: {method: 'GET', params: {type: 'track', market: 'GB'}}
    });
  }]);
