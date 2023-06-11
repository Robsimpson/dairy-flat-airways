let submit_button;
let outbound_segments;
let return_segments;
let outbound_legs_chosen = [];
let return_legs_chosen = [];
let checkboxes;

document.addEventListener('DOMContentLoaded', function setUpFormBehavoiurs() {

    submit_button = document.getElementById("bookFlights");
    outbound_segments = document.getElementById("outbound-must-choose");
    return_segments = document.getElementById("return-must-choose");
    addListenersToCheckBox();

});


function addListenersToCheckBox() {
    checkboxes = document.querySelectorAll('input[type=checkbox]');
    for (let i = 0; i < checkboxes.length; i++) {
        checkboxes[i].addEventListener('change', function () {
                            let selected_details = this.getAttribute('value').split('|');
                selected_details.push(this.getAttribute('name'));
                selected_details.push(selected_details[2].match(/\((.*?)\)/)[1]);
                selected_details.push(selected_details[4].match(/\((.*?)\)/)[1]);
            if (this.checked) {
                selectBasedOnDetails(selected_details);
            } else {
                console.log("unchecked");
                unSelectBasedOnDetails(selected_details);
            }
        });
    }
}

function selectBasedOnDetails(details) {
    if (details[details.length-3] ==='outbound_flight') {
        for (let i=0; i< outbound_segments.children.length; i++) {
            if (outbound_segments.children[i].dataset.origin === details[details.length-2] && outbound_segments.children[i].dataset.dest === details[details.length-1]) {
                outbound_legs_chosen.push([details[details.length - 2], details[details.length - 1]]);
                if (checkForDuplicates(outbound_legs_chosen)) {
                 outbound_segments.children[i].innerHTML = outbound_segments.children[i].innerHTML.replace(/:.*/g, "") + ": you have selected this leg more than once!"
                      outbound_segments.children[i].style.color = "red";
                } else {
                    outbound_segments.children[i].innerHTML.replace(/:.*/g, "");
                    outbound_segments.children[i].removeAttribute('style');
                    if (outbound_legs_chosen.length > 0) {
                        outbound_segments.children[i].classList.add("leg-selected");
                    } else {
                        outbound_segments.children[i].classList.remove("leg-selected");
                    }
                }

            }
        }
    } else {
                for (let i = 0; i < return_segments.children.length; i++) {
                    if (return_segments.children[i].dataset.origin === details[details.length - 2] && return_segments.children[i].dataset.dest === details[details.length - 1]) {
                        return_legs_chosen.push([details[details.length - 2], details[details.length - 1]]);
                        if (checkForDuplicates(return_legs_chosen)) {
                          return_segments.children[i].innerHTML = return_segments.children[i].innerHTML.replace(/:.*/g, "");
                             return_segments.children[i].style.color = "red";
                        } else {
                            return_segments.children[i].innerHTML.replace(/:.*/g, "");
                            return_segments.children[i].removeAttribute('style');
                    if (return_legs_chosen.length > 0) {
                        return_segments.children[i].classList.add("leg-selected");
                    } else {
                        return_segments.children[i].classList.remove("leg-selected");
                    }
                        }
                    }


                }

            }
    checkButton();
}

function unSelectBasedOnDetails(details) {
    if (details[details.length-3] ==='outbound_flight') {
        for (let i=0; i< outbound_segments.children.length; i++) {
            if (outbound_segments.children[i].dataset.origin === details[details.length-2] && outbound_segments.children[i].dataset.dest === details[details.length-1]) {
                outbound_legs_chosen = purgeFromArray(outbound_legs_chosen,[details[details.length - 2], details[details.length-1]]);
                if (checkForDuplicates(outbound_legs_chosen)) {
                    outbound_segments.children[i].innerHTML = outbound_segments.children[i].innerHTML.replace(/:.*/g, "") + ": you have selected this leg more than once!"
                    outbound_segments.children[i].style.color = "red";
                } else {
                    outbound_segments.children[i].innerHTML = outbound_segments.children[i].innerHTML.replace(/:.*/g, "");
                    outbound_segments.children[i].removeAttribute('style');
                    if (outbound_legs_chosen.length > 0) {
                        outbound_segments.children[i].classList.add("leg-selected");
                    } else {
                        outbound_segments.children[i].classList.remove("leg-selected");
                    }
                }

            }
        }
    } else {
                for (let i = 0; i < return_segments.children.length; i++) {
                    if (return_segments.children[i].dataset.origin === details[details.length - 2] && return_segments.children[i].dataset.dest === details[details.length - 1]) {
                        return_legs_chosen = purgeFromArray(return_legs_chosen,[details[details.length - 2], details[details.length-1]]);
                     if (checkForDuplicates(return_legs_chosen)) {
                            return_segments.children[i].innerHTML = return_segments.children[i].innerHTML.replace(/:.*/g, "") +": you have selected this leg more than once!"
                            return_segments.children[i].style.color = "red";
                        } else {
                         //using the regex here si risky (what if some place name ends up with a : in it), but it's pretty late and i'm tired
                            return_segments.children[i].innerHTML = return_segments.children[i].innerHTML.replace(/:.*/g, "");
                            return_segments.children[i].removeAttribute('style');
                    if (return_legs_chosen.length > 0) {
                        return_segments.children[i].classList.add("leg-selected");
                    } else {
                        return_segments.children[i].classList.remove("leg-selected");
                    }
                        }
                    }


                }

            }
    checkButton();
}



function checkForDuplicates(input_array) {
    if (input_array === null) {
        return false
    }

    let unique = new Set();

    for (let i = 0; i < input_array.length; i++) {

        if (unique.has(JSON.stringify(input_array[i]))) {
            return true;
        } else {
            unique.add(JSON.stringify(input_array[i]));
        }
    }
    return false;

}

function purgeFromArray(full_array,sub_array) {
    if (sub_array === null || full_array === null) {
        return full_array
    }
    for (let i=full_array.length-1; i>=0; i--) {
            if (JSON.stringify(full_array[i]) === JSON.stringify(sub_array)) {
                full_array.splice(i,1);
                return full_array;
            }
        }

    return full_array;

}

function checkButton() {

    let ok = false;
    console.log(outbound_legs_chosen.length);
    console.log(outbound_segments.childElementCount);
    ok = (outbound_legs_chosen.length === outbound_segments.childElementCount);
    console.log(ok);
    if (return_segments !== null) {
       ok = return_legs_chosen.length === return_segments.childElementCount && ok;
    }

    if (ok) {
        submit_button.removeAttribute('disabled','disabled');
        submit_button.innerHTML = "<h3>Ready to go!</h3>"
    } else {
        submit_button.setAttribute('disabled', 'disabled');
        submit_button.innerHTML = "<h3>Select valid legs!</h3>"
    }
}

function bookTheseFlights(passengers) {

    let booking = {};

    j = 0;
    for (let i = 0; i < checkboxes.length; i++) {
        // create an API post request
        if (checkboxes[i].checked) {
            let details = checkboxes[i].getAttribute('value').split("|");
            booking[j] = {
                "direction": checkboxes[i].getAttribute('name'),
                "flight": details[0],
                "leg": details[1],
                "price": parseInt(document.getElementById(details[0] + '-price').children[details[1]].innerHTML.replace(/\$/g,'')),
                "passengers": passengers,

            }
            j++;


        }
    }


    let json_booking = JSON.stringify(booking);
    const csrftoken = getCookie('csrftoken');

    fetch('/dfairways/book_flights/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'content-type': 'application/json'
        }, body: json_booking,
    }).then(response => {
        return response.text();
    }).then(html => {
        document.open();
        document.write(html);
        document.close();
        window.history.pushState(null, null, '/dfairways/book_flights/');
    }).catch(function (error) {
        console.log(error);
    });
}
function getCookie(name) {
  const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return cookieValue ? cookieValue.pop() : '';
}

function createBookings(outbound_flights,return_flights,passengers) {

    let booking = {}
    booking['first_name'] = document.getElementById('primary_name').value;
    booking['surname'] = document.getElementById('primary_surname').value;
    booking['email'] = document.getElementById('primary_email').value;
    booking['outbound'] = outbound_flights
    booking['return'] = return_flights
    booking['passengers'] = passengers

    let json_booking = JSON.stringify(booking);
    const csrftoken = getCookie('csrftoken');

    fetch('/dfairways/create_bookings/', {
     method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'content-type': 'application/json'
        }, body: json_booking,
    }).then(response => {
        return response.text();
    }).then(html => {

        window.location.href = '/dfairways/';
    }).catch(function (error) {
        console.log(error);
    });



}