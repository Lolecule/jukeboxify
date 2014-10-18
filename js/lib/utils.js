queryParams = function() {
  var url = document.URL;
  var queryString = url.split('?')[1].split('#')[0];
  var queryPairs = queryString.split('&');
  var params = {};
  for(pair in queryPairs) {
    var splitPair = pair.split('=');
    params[splitPair[0]] = splitPair[1];
  }
}
