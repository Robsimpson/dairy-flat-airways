let flights;

document.addEventListener('DOMContentLoaded', function fill_upcoming_schedule() {
    let schedule = document.getElementById("upcoming_schedule_display");
    let schedule_html = "<table><tr><th>Flight Number</th><th>Plane</th><th>Route</th><th>Status</th></tr>";

    fetch("/dfairways/get_scheduled_flight_json/?limit=10")
        .then(response => response.json())
        .then(function (data) {

            flights = data;
            for (let i = 0; i < flights.length; i++) {
                schedule_html += construct_table_row(flights[i]['fields']);
            }

            schedule.innerHTML = schedule_html + "</table>";

        })
        .catch(error => console.error(error));


});

function construct_table_row(flight) {
    let route_details_string = "";
    let row = "<tr>";
    row += "<td>" + flight.flight_number + "</td>";
    row += "<td>" + flight.plane + "</td>";
    for (let i = 0; i < flight.route_details.length; i++) {
        route_details_string += flight.route_details[i][0] + "(" + Date(flight.route_details[i][1]).toLocaleString() + ")";
    }
    row += "<td>" + route_details_string + "</td>";
    row += "<td>" + flight.status + "</td>";
    row += "</tr>";
    console.log(row);
    return row;
}