let airport_markers = [];
let route_lines = {};
let airports = {};
let airport_coords = {};
let routes = {};
let map = null;

document.addEventListener('DOMContentLoaded', function init_map() {

    mapboxgl.accessToken = 'pk.eyJ1Ijoic2ltcHNyb2IiLCJhIjoiY2xpaXFsa2J4MDB0ZzNob2txNjZsZmU4dyJ9.7r75o7OetaIIQDIzdfL0mg';

    map = new mapboxgl.Map({
        container: 'flight-position-map', // container ID
        style: 'mapbox://styles/simpsrob/climnc2cb005501pw2bt54e6y', // style URL
        center: [165.421, -43.429], // starting position [lng, lat]
        pitch: 25,
        bearing:-10,
        zoom: 3.5, // starting zoom
        projection: 'mercator'

    });
    fill_map()

});
function fill_map() {

    map.on('style.load', function () {
        draw_airports();
        draw_lines().then(r => console.log("done - lines"));
        draw_flights().then(r => console.log("done - flights"));
    });
}

function poor_mans_spin_lock() {
    return new Promise((resolve) => {

        let interval = setInterval(function () {
            if (airports == 'undefined' || airports.length === 0) {
            } else {
                resolve('got airports');
                clearInterval(interval);
            }} , 500);
    });
}

function draw_airports() {

        fetch("/dfairways/get_airport_json/")
            .then(response => response.json())
            .then(data => {
                airports = data;
                for (let i = 0; i < data.length; i++) {
                    let airport = data[i];
                    //this is stored as a list, because this is how it is used in the route data
                    airport_coords[airport.pk] = [airport.fields.long, airport.fields.lat];

                    let marker = new mapboxgl.Marker()
                        .setLngLat([airport.fields.long, airport.fields.lat])
                        .setPopup(new mapboxgl.Popup({offset: 25}) // add popups
                            .setHTML('<h5>' + airport.fields.name + '</h5>'))
                        .addTo(map);
                    airport_markers.push(marker);
                }


            })
            .catch(error => console.error(error));

}

async function draw_lines() {
    try {
        await poor_mans_spin_lock();
        fetch("/dfairways/get_active_schedule_json/")
            .then(response => response.json())
            .then(data => {
                routes = data;
                for (let i = 0; i < routes.length; i++) {

                    let route = routes[i];
                    let start_point = turf.point(airport_coords[route.fields.origin])
                    let end_point = turf.point(airport_coords[route.fields.destination])

                    let curved_line = turf.greatCircle(start_point, end_point, {properties: {name: route.fields.name}});
                    map.addSource("line" + i, {
                        type: 'geojson',
                        data: curved_line
                    })
                    map.addLayer({
                        'id': 'line' + i,
                        'type': 'line',
                        'source': 'line' + i,
                        'paint': {
                            'line-color': '#05ADF0',
                            'line-width': 1
                        }
                    })

                }
            })
            .catch(error => console.error(error));
    } catch (e) {
        console.error(e);
    }
}

function updateFlights() {

    fetch("/dfairways/trigger_update_flight_status/")
        .then(response => console.log('Updated'))
        .catch(error => console.error(error));
}

async function draw_flights() {
    try {
        await poor_mans_spin_lock();
        fetch("/dfairways/get_aircraft_locations/")
            .then(response => response.json())
            .then(data => {

                // draw each of the flights on the line of their route, with their position
                let plane_tail = Object.keys(data);
                console.log(plane_tail)

                for (let i = 0; i< plane_tail.length; i++) {
                    let plane = plane_tail[i];
                    let flight = data[plane];
                    console.log(flight);
                    if (flight.progress < 1) {
                        console.log('drawing flight ' + flight.origin + ' to ' + flight.destination + ' at ' + flight.progress)
                        //only add the flight line if it is in progress
                        let start_point = turf.point(airport_coords[flight.origin]);
                        let end_point = turf.point(airport_coords[flight.destination]);
                        let curved_line = turf.greatCircle(start_point, end_point, {properties: {name: plane}});
                        let kms_prog = turf.length(curved_line, {units: 'kilometers'}) * flight.progress;
                        let flight_position = turf.along(curved_line, kms_prog, {units: 'kilometers'});

                        let progress_line = turf.greatCircle(start_point,flight_position, {properties: {name: plane}});

                        // draw the inflight segment in red
                        map.addSource('flight_line'+i, {
                            type: 'geojson',
                            data: progress_line,
                        })
                        map.addLayer({
                            'id': 'flight_line' + i,
                            'type': 'line',
                            'source': 'flight_line' + i,
                            'paint': {
                                'line-color': '#C41E3A',
                                'line-width': 3
                            }
                        })

                    } else {
                        let flight_position = turf.point(airport_coords[flight.destination]);
                    }
                    // and we always add the plane symbol
                    let marker = new mapboxgl.Marker();
                }

            })
            .catch(error => console.error(error));
    } catch (e) {
        console.error(e);
    }

}

setInterval(updateFlights, 60000)
setInterval(draw_flights, 60000)