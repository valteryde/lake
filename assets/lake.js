
/* HELP */
function xmpGET(url, callback=function(){}) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    //console.log(this.readyState, this.status)

    if (this.readyState == 4 && this.status == 200) {
      callback();
    }
  };
  xhttp.open("GET", url, true);
  xhttp.send();
}


/* WEBSOCKET */

//start websocket with the backend.
function startWebSocket() {

  var socket = new WebSocket("ws://localhost:8765");
  socket.onopen = function() {
    socket.send('[welcome]');
    window.remote = new Remote(socket)
  };
  socket.onmessage = function(s) {
    var msg = s.data
    if (msg.slice(msg.indexOf('[')+1,4).toLowerCase() == 'exe') window.remote._executeFunction_(msg.slice(msg.indexOf('(')+1,msg.indexOf(')')));
  };
  return socket
}

//when switching page use this function
//This is instead done by catching the get request

/*
const change = url => {
  socket.send('[SWITCHING]')
  window.location = url;
};*/


/* REMOTE */
class Remote {
  constructor(socket) {

    this.socket = socket

  }

  do(com) {

    //i do not know why sending [execute] closes the server but it does...
    this.socket.send('[exe]('+com+')')
  }


  _executeFunction_(funcname) {
    try {
        window._exposedFunctions_[funcname]();
    } catch (e) {
      console.warn(e);
    }
  }

}

/* EXPOSE FUNCTION */
window._exposedFunctions_ = {};
const expose = func => {
  window._exposedFunctions_[func.name] = func
}



/* MAIN */
window.socket = startWebSocket();
