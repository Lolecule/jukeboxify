'use strict';

var jukeboxifyControllers = angular.module('jukeboxifyControllers', []);

jukeboxifyControllers.controller('TrackCtrl', ['$scope', 'Spotify',
  function($scope, Spotify) {
    $scope.search = function(query) {
      if(query === "") {
        $scope.tracks = []
      } else {
        Spotify.search({q: query}, function(result) {
          $scope.tracks = result.tracks.items;
        });
      };
    };

    $scope.artistString = function(track) {
      var artistNames = track.artists.map(function(artist, index, array) {
        return artist.name;
      });

      return artistNames.join(", ");
    };
}]);
