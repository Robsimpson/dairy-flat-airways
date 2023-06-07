let flights;

document.addEventListener('DOMContentLoaded', function fill_upcoming_schedule() {
    let schedule = document.getElementById("upcoming_schedule_display");
    let schedule_html = "<table><tr><th>Flight</th><th>Plane</th><th>Route</th><th>Status</th></tr>";

    fetch("/dfairways/get_scheduled_flight_json/?limit=8&status=Scheduled,Delayed,Go%20to%20gate,Boarded)")
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

    let options = {
        day: '2-digit',
        month: '2-digit',
        year: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };

    let formatter = new Intl.DateTimeFormat('en-GB', options);

    let route_details_string = "";
    let row = "<tr>";
    row += "<td>" + flight.flight_number + "</td>";
    row += "<td>" + flight.plane + "</td>";
    for (let i = 0; i < flight.route_details.length; i++) {
        let temp_date =  new Date(flight.route_details[i][1]*1000);
        let origin_word = i > 0 ? "Depart: " : "Origin: ";
        let dest_word = i < flight.route_details.length-1  ? "Pickup: " : "Dest: ";
        route_details_string += origin_word + flight.route_details[i][0] + ": " + formatter.format(temp_date) + "<BR>";
        temp_date = new Date(flight.route_details[i][3]*1000);
        route_details_string += dest_word + flight.route_details[i][2] + ": " + formatter.format(temp_date) + " ";

    }
    row += "<td>" + route_details_string + "</td>";
    row += "<td>" + flight.status + "</td>";
    row += "</tr>";
    console.log(row);
    return row;
}