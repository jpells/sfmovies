var Search = function(options) {
    this.form_selector = options.form_selector
    this.url = options.url || '/films/'
    this.delay = parseInt(options.delay || 300)
    this.minimum_length = parseInt(options.minimum_length || 2)
    this.form_elem = null
    this.query_box = null
    this.data = null
    this.map_options = {}
    this.map = null
    this.markers = []
    this.open_infowindow = null
}

Search.prototype.setup = function() {
    var self = this
    this.form_elem = $(this.form_selector)
    this.query_box = this.form_elem.find('input[name=query]')
    //Create map
    this.map_options = {
        center: new google.maps.LatLng(37.7749295, -122.4194155),
        zoom: 12,
    }
    this.map = new google.maps.Map(document.getElementById("map-canvas"), self.map_options)
    self.get_films()
    // Watch the input box.
    this.query_box.on('keyup', function() {
        var query = self.query_box.val()
        if (query.length == 0) {
            //Get all films if query box goes back to empty
            self.get_films()
        } else if (query.length >= self.minimum_length) {
            //Get films via query
            self.fetch(query)
        }
    })
    //On selecting a result filter out all other results
    this.form_elem.on('click', '.result', function(ev) {
        self.query_box.val($(this).text())
        self.get_film($(this).text())
    })
    //On selecting reset get all films
    this.form_elem.find('input[type=reset]').on('click', function() {
        self.get_films()
    })
}

Search.prototype.get_films = function() {
    var self = this
    $.ajax({
        url: this.url,
        success: function(data) {
            self.data = data
            self.show_results()
        },
    })
}

Search.prototype.get_film = function(title) {
    var self = this
    $.ajax({
        url: this.url,
        data: {
            'title': title,
        },
        success: function(data) {
            self.data = data
            self.show_results()
        },
    })
}

Search.prototype.fetch = function(query) {
    var self = this
    $.ajax({
        url: this.url,
        data: {
            'query': query,
        },
        success: function(data) {
            self.data = data
            self.show_results()
        },
    })
}

Search.prototype.show_results = function() {
    var self = this
    //Remove any existing results.
    $('.results').remove()
    for (var marker_offset in self.markers) {
        self.markers[marker_offset].setMap(null)
    }
    //Add results and markers
    self.markers = []
    var results = self.data.results || []
    var results_wrapper = $('<div class="results"></div>')
    var base_elem = $('<div><a href="#" class="result"></a></div>')
    if (results.length > 0) {
        for (var res_offset in results) {
            var elem = base_elem.clone()
            elem.find('.result').text(results[res_offset].title)
            results_wrapper.append(elem)
            self.plot_film(results[res_offset])
        }
    } else {
        var elem = base_elem.clone()
        elem.text("No results found.")
        results_wrapper.append(elem)
    }
    this.form_elem.find('input[type=reset]').after(results_wrapper)
}

Search.prototype.create_marker = function(film, film_location) {
    var self = this
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(film_location.lat, film_location.lng),
        map: self.map,
        title: film.title,
    })
    self.create_info_window(marker, film, film_location)
    self.markers.push(marker)
}

Search.prototype.create_info_window = function(marker, film, film_location) {
    var self = this
    var content_string = "<h5>"+film.title+" ("+film.release_year+
        ")</h5><h6>"+film_location.address+
        "</h6><p><b>Director:</b> "+film.director+"</p>"
    if (film.writer) {
        content_string += "<p><b>Writer:</b> "+film.writer+"</p>"
    }
    content_string += "</p><p><b>Actors:</b> "+film.actors+"</p>"
    if (film.fun_facts) {
        content_string += "<p><b>Fun Facts:</b> "+film.fun_facts+"</p>"
    }
    content_string += "</p><p><b>Production Company:</b> "+film.production_company+"</p>"
    if (film.distributor) {
        content_string += "<p><b>Distributor:</b> "+film.distributor+"</p>"
    }
    var infowindow = new google.maps.InfoWindow({
        content: content_string,
    })
    google.maps.event.addListener(marker, 'click', function() {
        if (self.open_infowindow) {
            self.open_infowindow.close();
        }
        infowindow.open(self.map, marker)
        self.open_infowindow = infowindow
    })
}

Search.prototype.plot_film = function(film) {
    var self = this
    for (var film_location_offset in film.film_locations) {
        var film_location = film.film_locations[film_location_offset]
        if (film_location.lat != 0 && film_location.lng != 0) {
            self.create_marker(film, film_location)
        }
    }
}