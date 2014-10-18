User = Backbone.Model.extend({
  urlRoot: 'https://api.spotify.com/v1',
  defaults: {
    id: 'me'
  }
  initialize: function() {
    var params = queryParams();
    if (params.access_token != null) {
      this.set({ token: params.access_token })
    }
  }
});

var user = new User();
var authHeader = {'Authorization': 'Bearer ' + user.get("token")};
user.fetch({
  headers: authHeader,
  success: function(user) {
    alert("Hello! " + user.get("display_name"))
  }
})
