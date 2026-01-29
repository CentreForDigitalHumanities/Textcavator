var url = new URL(window.location);
var corpus = url.searchParams.get('corpus');

var appUrl = new URL('http://localhost:4200');
if (corpus) {
    appUrl.pathname = `/search/${corpus}/`;
}

var iframe = document.getElementById('textcavator-iframe');
iframe.setAttribute('src', appUrl.toString());
