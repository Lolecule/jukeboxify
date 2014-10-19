fragmentParams = function() {
  var url = document.URL;
  var fragmentString = url.split('#')[1];
  var fragmentPairs = fragmentString.split('&');
  console.log(fragmentPairs);
  var params = {};
  for(var index in fragmentPairs) {
    var pair = fragmentPairs[index];
    var splitPair = pair.split('=');
    console.log(splitPair[0]);
    console.log(splitPair[1]);
    params[splitPair[0]] = splitPair[1];
  }
  return params;
};
